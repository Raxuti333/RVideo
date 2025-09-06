from flask import Flask, session, redirect, url_for, request, flash, get_flashed_messages
from parse import cut, wash, validate
from werkzeug.security import generate_password_hash
import db

def no_match(html, unused) -> str:
    return cut(html, "NO_MATCH")

def exists(html: str, username: str):
    return cut(html.replace("$USERNAME", username), "EXISTS")

def signup_page(app: Flask):
    html: str = open(app.root_path + "/html/signup.html").read()
    
    if session.get("profile") != None:
        return wash(cut(html, "PROFILE"))
    html = cut(html, "NO_PROFILE")

    list = get_flashed_messages()
    if list != []:
        JTABLE: dict[str, int] = { "NO_MATCH": no_match, "EXISTS": exists }
        html = JTABLE[list[0]](html, list[-1])

    html = wash(html)
    return html

# this is run in try expect block so failing is fine
def signup_create(app: Flask):
    username = validate(request.form["username"])
    password = request.form["password"]
    c_pass   = request.form["confirm_password"]

    if password != c_pass:
        flash("NO_MATCH")
        return redirect(url_for("signup"), 303)
    
    # Check if username is taken
    if db.query("SELECT COUNT(username) FROM profile WHERE username = ?", (username,))[0] != 0:
        flash("EXISTS")
        flash(username)
        return redirect(url_for("signup"), 303)

    # Create new profile
    db.query("INSERT INTO profile (username, password) VALUES(?, ?)", (username, generate_password_hash(password)))

    return redirect(url_for("profile"), 303)