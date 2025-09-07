from flask import Flask, session, request, send_file, redirect, flash, get_flashed_messages
from parse import cut, wash
import os
from io import BytesIO
import db

def pid_get() -> str | None:
    try:
        return hex(int(db.query("SELECT pid FROM profile WHERE username = ?", (session["profile"]["username"],))[0][0]))
    except:
        return None
    
def file_get() -> str | None:
    pid: str = pid_get()
    if pid == None:
        return None

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
    if list != []:
        pass
    
    html = html.replace("$TOKEN", session["profile"]["token"])
    html = wash(html)
    return html

# Support profile pictures
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
    
    pid: str = pid_get()
    if pid == None:
        flash("DB_FAIL")
        return redirect("/")

    # remove old pfp
    for file in os.listdir("pfp"):
        if pid == file.split(".")[0]:
            os.remove("pfp/" + file)
            break

    picture.save("pfp/" + pid + "." + type)

    flash("SUCCESS")
    return redirect("/profile")
