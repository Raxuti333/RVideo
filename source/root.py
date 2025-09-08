from flask import Flask, session, request, send_file, redirect, flash, get_flashed_messages
from parse import cut, wash, search

def root_page(app: Flask):
    html: str = open(app.root_path + "/html/root.html").read()

    if session.get("profile") != None:
        html = cut(html.replace("$USERNAME", session["profile"]["username"]).replace("$PID", str(session["profile"]["pid"])), "PROFILE")
    else:
        html = cut(html, "LOGIN")

    embed: str = ""

    req = request.form.get("search")
    if req == None:
        embed = search("BEFORE=now")
    else:
        embed = search(req)

    return wash(html.replace("$VIDEOS", embed))

def root_favicon(app: Flask):
    return send_file(app.root_path + "/images/favicon.ico", mimetype='image/vnd.microsoft.icon')
