from flask import Flask, session, redirect, request, flash, get_flashed_messages
from parse import cut, wash, validate
from werkzeug.security import check_password_hash
from secrets import token_hex
import db

def login_page(app: Flask):
    html: str = open(app.root_path + "/html/login.html").read()

    if session.get("profile") != None:
        return redirect("/")
    
    list = get_flashed_messages()
    if list != []:
        if list[0] == "NO_MATCH":
            html = cut(html, "NO_MATCH")
        elif list[0] == "INVALID":
            html = cut(html, "INVALID")

    html = wash(html)
    return html

def login_in(app: Flask):
    try:
        username = validate(request.form["username"])
        password = request.form["password"]
    except:
        flash("INVALID")
        return redirect("/login")

    profile = db.query("SELECT password FROM profile WHERE username = ?", (username,))
    
    if profile == []:
        flash("NO_MATCH")
        return redirect("/login")

    if not check_password_hash(profile[0][0], password):
        flash("NO_MATCH")
        return redirect("/login")

    session["profile"] = { "username": username, "token": token_hex(16) }

    return redirect("/")