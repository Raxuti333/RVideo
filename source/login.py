""" Handle login, logout and signup requests """

from flask import render_template, redirect
from werkzeug.security import generate_password_hash, check_password_hash
from util import get_token, get_account, set_account, check_username, clear_account
from util import get_form, get_flash, set_flash, get_method, get_query, check_password
from db import db

def login(user: dict, form: dict):
    """ process login form """

    if not check_password_hash(user["password"], form["password"]):
        set_flash(["incorrect password", "#ff0033"])
        return redirect("/login")

    set_account({"pid": user["pid"], "username": user["username"]})

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

    verdict = check_username(form["username"])
    if not verdict[0]:
        set_flash([verdict[1], "#ff0033"])
        return redirect("/login#signup")

    db.query(
    "INSERT INTO profile (username, password, timestamp, date) "
    "VALUES(?, ?, unixepoch('now'), date('now'))",
    [form["username"], generate_password_hash(form["password"])],
    0
    )

    set_flash(["account succesfully created!", "#00b500"])
    return redirect("/login")

def handle_form(token: str):
    """ Handle form and select signup or login """

    target: dict = { False: "/login#", True: "/login#signup" }

    form = get_form([
                     ("username", str),
                     ("password", str),
                     ("chckpswd", str),
                     ("signup",   bool),
                     ("token",    str),
                    ])

    if form["token"] != token:
        set_flash(["CSRF ERROR", "#ff0033"])
        return redirect(target[form["signup"]])

    user = db.query("SELECT pid, username, password FROM profile WHERE username = ?",
                    [form["username"]])

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
        return redirect(target[form["signup"]])

    if form["signup"]:
        return signup(form)
    return login(user, form)


def login_page():
    """ serve page or process form """

    flash   = get_flash()
    token   = get_token()
    account = get_account()

    if account is not None:
        if get_query("=")[0] == "out":
            clear_account()
            return redirect("/")

        return redirect("/account?page=" + str(account["pid"]))

    if get_method() == "POST":
        return handle_form(token)

    return render_template("login.html", token = token, message = flash)
