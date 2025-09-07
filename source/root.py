from flask import Flask, session, request, send_file, redirect, flash, get_flashed_messages
from parse import cut, wash
import db

def root_favicon(app: Flask):
    return send_file(app.root_path + "/images/favicon.ico", mimetype='image/vnd.microsoft.icon')

def root_page(app: Flask):
    html: str = open(app.root_path + "/html/root.html").read()

    if session.get("profile") != None:
        html = cut(html.replace("$USERNAME", session["profile"]["username"]).replace("$PID", str(session["profile"]["pid"])), "PROFILE")
    else:
        html = cut(html, "LOGIN")

    embed: str = ""

    search = request.form.get("search")
    if search == None:
        videos = db.query("SELECT * FROM video ORDER BY datetime(date) DESC LIMIT 20", count=20)
        for v in videos:
            embed += "<a href=\"video?view=" + str(v["vid"]) + "\"><div style=\"display: inline-block; margin: 15px\">" + "<img src=\"profile?pfp=" + str(v["pid"]) + "\" style=\"display: inline-block; width: 48px; height: 48px;\"><p style=\"display: inline-block;\">" + v["name"] + "<p></div></a>"

    return wash(html.replace("$VIDEOS", embed))