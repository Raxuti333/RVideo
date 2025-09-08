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

# TODO add commenting and comment view
def video_view(app: Flask):
    # Replace with non-garbage collection reliant method
    html: str = open(app.root_path + "/html/view.html").read()

    vid: str = str(request.query_string, "utf-8").split("=")[-1]

    if not vid.isdigit():
        return redirect("/")
    
    if session.get("profile") != None:
        html = cut(html.replace("$PID", str(session["profile"]["pid"])).replace("$USERNAME", session["profile"]["username"]), "PROFILE")
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