from flask import Flask, session, request, send_file, redirect, flash, get_flashed_messages, abort
from parse import cut, wash, validate
import os
from io import BytesIO
import db

def file_get(pid: str) -> str | None:
    v: str = None
    for type in ["mp4", "avi", "webm"]:
        if os.path.isfile("video/" + pid + "." + type):
            v = "video/" + pid + "." + type
    return v

def video_edit(app: Flask):
    # Replace with non-garbage collection reliant method
    html: str = open(app.root_path + "/html/edit.html").read()

    if session.get("profile") == None:
        return redirect("/")

    key: str = str(request.query_string, "utf-8").split("=")[-1]
    if not key.isdigit():
        return abort(404)
    
    vid = int(key)
    video = db.query("SELECT * FROM video WHERE vid = ?", [vid])

    if video == []:
        return abort(404)
    
    if video[0]["pid"] != session["profile"]["pid"]:
        return abort(401)
    
    html = html.replace("$PID", str(session["profile"]["pid"])).replace("$USERNAME", session["profile"]["username"]).replace("$TITLE", video[0]["name"]).replace("$DESCRIPTION", video[0]["description"]).replace("$TOKEN", session["profile"]["token"]).replace("$VID", str(vid))
    return html

def video_update(app: Flask):
    if session.get("profile") == None:
        return abort(401)
    
    key: str = str(request.query_string, "utf-8").split("=")[-1]
    if not key.isdigit():
        return abort(404)
    
    vid = int(key)
    video = db.query("SELECT * FROM video WHERE vid = ?", [vid])
    
    if video == []:
        return abort(404)
    
    if video[0]["pid"] != session["profile"]["pid"]:
        return abort(401)
    
    token = request.form.get("token")
    delete = request.form.get("delete")

    if token != session["profile"]["token"]:
        return abort(400)

    if delete != None:
        if delete == "True":
            db.query("DELETE FROM video WHERE vid = ?", [vid])
            os.remove(file_get(hex(vid)))
        return redirect("/profile")
    
    title = request.form.get("title")
    description = request.form.get("description")

    if title == None or description == None:
        flash("INVALID")
        return redirect("/video?edit=" + str(vid))
    
    title = validate(title)
    description = validate(description)
    
    if len(title) == 0 or len(title) > 128:
        flash("WRONG_TITLE")
        return redirect("/video?edit=" + str(vid))
    
    db.query("UPDATE video SET name = ?, description = ? WHERE vid = ?", [title, description, vid])

    return redirect("/video?view=" + str(vid))

# TODO add commenting and comment view
def video_view(app: Flask):
    # Replace with non-garbage collection reliant method
    html: str = open(app.root_path + "/html/view.html").read()

    vid: str = str(request.query_string, "utf-8").split("=")[-1]

    if not vid.isdigit():
        return redirect("/")
    
    if session.get("profile") != None:
        html = cut(html.replace("$PID", str(session["profile"]["pid"])).replace("$USERNAME", session["profile"]["username"]), "PROFILE")
        if vid.isdigit():
            pid: int = db.query("SELECT pid FROM video WHERE vid = ?", [int(vid)])[0][0]
            if session["profile"]["pid"] == pid:
               html = cut(html, "OWNER")
    else:
        html = cut(html, "LOGIN")

    row: int = db.query("SELECT pid, name, description FROM video WHERE vid = ?", [int(vid)])[0]
    auth_username: str = db.query("SELECT username FROM profile WHERE pid = ?", [row["pid"]])[0][0]

    html = wash(html.replace("$VID", vid).replace("$AUTH_PID", str(row["pid"])).replace("$AUTH_USERNAME", auth_username)).replace("$TITLE", row["name"]).replace("$DESCRIPTION", row["description"])
    return html

def video_page(app: Flask):
    # Replace with non-garbage collection reliant method
    html: str = open(app.root_path + "/html/video.html").read()

    if session.get("profile") == None:
        return redirect("/login")
    
    list = get_flashed_messages()
    if list != [] and list[0] in ["INVALID", "NO_SELECTED", "WRONG_TITLE", "NO_SUPPORT"]:
        html = cut(html, list[0])
    
    html = html.replace("$USERNAME", session["profile"]["username"]).replace("$PID", str(session["profile"]["pid"])).replace("$TOKEN", session["profile"]["token"])
    return wash(html)

def video_upload(app: Flask):
    if session.get("profile") == None:
        return redirect("/")

    try:
        video       = request.files["video"]
        title       = validate(request.form["title"])
        description = validate(request.form.get("description"))
        token       = request.form["token"]
    except:
        flash("INVALID")
        return redirect("/video")
    
    # CSRF protection
    if token != session["profile"]["token"]:
        return redirect("/")
    
    if video.filename == "":
        flash("NO_SELECTED")
        return redirect("/video")
    
    if len(title) == 0 or len(title) > 128:
        flash("WRONG_TITLE")
        return redirect("/video")
    
    type: str = video.filename.split(".")[-1]

    if not type in ["mp4", "avi", "webm"]:
        flash("NO_SUPPORT")
        return redirect("/video")
    
    vid: int = db.query("INSERT INTO video (pid, name, description, date) VALUES(?, ?, ?, datetime('now')) RETURNING vid", [session["profile"]["pid"], title, description])[0][0]

    video.save("video/" + hex(vid) + "." + type)

    return redirect("/video?view=" + str(vid))

def video_download(app: Flask):
    query: str = str(request.query_string, "utf-8").split("=")[-1]

    if not query.isdigit():
        return send_file(app.root_path + "/images/no-pfp.png", mimetype='image/png')
    
    vid: str = hex(int(query))

    video: str = file_get(vid)
    if video == None:
        return abort(404)
    
    MIMETYPE: {str, str} = {"mp4": "video/mp4", "avi": "video/x-msvideo", "webm": "video/webm"}

    # TODO implement streaming
    with open(video, "rb") as f:
        return send_file(BytesIO(f.read()), mimetype=MIMETYPE[video.split(".")[1]])