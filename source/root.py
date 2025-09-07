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

    html = wash(html)
    return html