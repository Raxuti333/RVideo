""" Handle login, logout and signup requests """


from flask import render_template, redirect
from werkzeug.security import generate_password_hash
from util import get_session_token, get_account, get_form, get_flash, set_flash, get_query, check_password
import db

def login(user, form: dict):
    """ TODO """
    return redirect("/")

def signup(form: dict):
    """ process signup form """

    verdict = check_password(form["password"])
    if not verdict[0]:
        set_flash([verdict[1], "#ff0033"])
        return redirect("/login#signup")

    if form["password"] != form["chckpswd"]:
        set_flash(["passwords don't match", "#ff0033"])
        return redirect("/login#signup")

    if len(form["username"]) == 0:
        set_flash(["username too short", "#ff0033"])
        return redirect("/login#signup")

    db.query("INSERT INTO profile (username, password) VALUES(?, ?)",
             [form["username"], generate_password_hash(form["password"])],
             0)

    set_flash(["account succesfully created!", "#ff0033"])
    return redirect("/login")

def handle_form(token: str):
    """ TODO """
    target: dict = { True: "#signup", False: "#" }

    form = get_form([
                     ("username", str),
                     ("password", str),
                     ("chckpswd", str),
                     ("signup",   bool),
                     ("token",    str),
                    ])

    if form["token"] != token:
        set_flash(["CSRF ERROR", "#ff0033"])
        return redirect("/login" + target[form["signup"]])

    user = db.query("SELECT password FROM profile WHERE username = ?", [form["username"]])

    # Truth table
    # !user | signup | value
    #   F   |   T    |   T
    #   T   |   T    |   F
    #   F   |   F    |   F
    #   T   |   F    |   T
    if (user is None) ^ form["signup"]:
        error: dict[bool, str] = {
            False: "user does not exist",
            True: "username is already taken"
            }
        set_flash([error[form["signup"]], "#ff0033"])
        return redirect("/login" + target[form["signup"]])

    if form["signup"]:
        return signup(form)
    else:
        return login(user, form)


def login_page():
    """ TODO """

    flash   = get_flash()
    token   = get_session_token()
    account = get_account()
    query   = get_query()

    if account is not None:
        return redirect("/account")

    if query[0] == "form":
        return handle_form(token)

    return render_template("login.html", token = token, message = flash)
