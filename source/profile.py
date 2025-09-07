from flask import Flask, session, request, send_file, redirect, flash, get_flashed_messages
from parse import cut, wash
import os
from io import BytesIO
import db

def file_get() -> str | None:
    pid: str = hex(session["profile"]["pid"])

    v: str = None
    for type in ["png", "jpg", "ico", "bmp"]:
        if os.path.isfile("pfp/" + pid + "." + type):
            v = "pfp/" + pid + "." + type
    return v

def profile_page(app: Flask):
    # Replace with non-garbage collection reliant method
    html: str = open(app.root_path + "/html/profile.html").read()

    if session.get("profile") == None:
        return redirect("/")

    list = get_flashed_messages()
    if list != [] and list[0] in ["SUCCESS", "NO_SELECTED", "NO_SUPPORT", "NO_CHANGES", "NO_CHANGES"]:
        html = cut(html, list[0])

    html = html.replace("$TOKEN", session["profile"]["token"]).replace("$USERNAME", session["profile"]["username"])
    html = wash(html)
    return html

def profile_picture(app: Flask):
    if session.get("profile") == None:
        return send_file(app.root_path + "/images/no-pfp.png", mimetype='image/png')
    
    picutre: str = file_get()
    if picutre == None:
        return send_file(app.root_path + "/images/no-pfp.png", mimetype='image/png')
    
    TABLE: {str, str} = {"png": "image/png", "jpg": "image/jpeg", "ico": "image/vnd.microsoft.icon", "bmp": "image/bmp"}

    with open(picutre, "rb") as f:
        return send_file(BytesIO(f.read()), mimetype=TABLE[picutre.split(".")[1]])

def profile_upload(app: Flask):
    if session.get("profile") == None:
        return redirect("/")

    try:
        picture = request.files["picture"]
        token   = request.form["token"]
    except:
        flash("INVALID")
        return redirect("/profile")
    
    # CSRF protection
    if token != session["profile"]["token"]:
        return redirect("/")
    
    if picture.filename == "":
        flash("NO_SELECTED")
        return redirect("/profile")
    
    type: str = picture.filename.split(".")[-1]

    if not type in ["png", "jpg", "ico", "bmp"]:
        flash("NO_SUPPORT")
        return redirect("/profile")

    old: str = file_get()
    if old != None:
        os.remove(file_get())

    picture.save("pfp/" + hex(session["profile"]["pid"]) + "." + type)

    flash("SUCCESS")
    return redirect("/profile")

def profile_edit(app: Flask):
    if session.get("profile") == None:
        return redirect("/")

    try:
        new_username = request.form["username"]
        token        = request.form["token"]
    except:
        flash("INVALID")
        return redirect("/profile")
    
    # CSRF protection
    if token != session["profile"]["token"]:
        return redirect("/")
    
    if new_username == session["profile"]["username"]:
        flash("NO_CHANGES")
        return redirect("/profile")

    # TODO check if this can raise exception
    v = db.query("SELECT COUNT(username) FROM profile WHERE username = ?", (new_username,))[0][0]

    if v != 0:
        flash("TAKEN")
        return redirect("/profile#edit_username")
    
    db.query("UPDATE profile SET username = ? WHERE pid = ?;", (new_username, session["profile"]["pid"]))
    session["profile"] = { "pid": session["profile"]["pid"], "username": new_username, "token": session["profile"]["token"] }

    return redirect("/profile")