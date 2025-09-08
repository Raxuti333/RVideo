from flask import Flask, session, redirect, request, flash, get_flashed_messages
from parse import cut, wash, validate
from werkzeug.security import generate_password_hash
import db

def no_match(html: str, unused) -> str:
    return cut(html, "NO_MATCH")

def exists(html: str, username: str) -> str:
    return cut(html.replace("$USERNAME", username), "EXISTS")

def invalid(html: str, unused) -> str:
    return cut(html, "INVALID")

def signup_page(app: Flask):
    html: str = open(app.root_path + "/html/signup.html").read()
    
    if session.get("profile") != None:
        return redirect("/")

    list = get_flashed_messages()
    if list != []:
        try:
            JTABLE: dict[str, int] = { "NO_MATCH": no_match, "EXISTS": exists, "INVALID": invalid }
            html = JTABLE[list[0]](html, list[-1])
        except:
            pass

    html = wash(html)
    return html

def signup_create(app: Flask):
    try:
        username = validate(request.form["username"])
        password = request.form["password"]
        c_pass   = request.form["confirm_password"]
    except:
        flash("INVALID")
        return redirect("/signup")

    if password != c_pass:
        flash("NO_MATCH")
        return redirect("/signup", 303)
    
    # Check if username is taken
    v = db.query("SELECT COUNT(username) FROM profile WHERE username = ?", [username])[0][0]
    if v != 0:
        flash("EXISTS")
        flash(username)
        return redirect("/signup", 303)

    # Create new profile
    db.query("INSERT INTO profile (username, password) VALUES(?, ?)", [username, generate_password_hash(password)])

    return redirect("/login", 303)