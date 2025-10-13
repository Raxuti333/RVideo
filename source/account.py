""" account.html and accounts_search.html rendering and form handling """

from os import remove
from flask import render_template, redirect
from werkzeug.security import generate_password_hash, check_password_hash
from util import get_query, get_filename, get_form, check_file, config
from util import set_flash, get_flash, check_password, check_username
from util import get_token, set_account, get_account, clear_account
from db import db

LIMIT = 20

def page():
    """ account page and sub resource routing """

    query = get_query("=")
    account = get_account()

    table: dict = { "page": profile, "edit": edit }
    execute = table.get(query[0])
    if execute is not None:
        return execute(query, account)

    condition: dict = {
        True: "WHERE LOWER(username) LIKE LOWER(?)",
        False: "ORDER BY pid DESC"
        }

    select: bool = query[0] == "search"

    accounts = db.query(
    "SELECT pid, username FROM profile " + 
    condition[select] + f" LIMIT { LIMIT }",
    [query[-1] + "%"] if select else [],
    LIMIT
    )

    return render_template(
    "search.html",
    account = account,
    accounts = accounts
    )

def profile(query: list[str], account: dict | None):
    """ profile page """

    pid: int = -1
    if account is not None:
        pid = account["pid"]

    token = get_token()
    error = get_flash()
    target = db.query("SELECT pid, username, date FROM profile WHERE pid = ?", [query[-1]])

    if target is None:
        return redirect("/")

    condition: str = " AND private = 0"
    if target["pid"] == pid:
        condition = ""

    videos = db.query(
    "SELECT vid, name, pid, private FROM video WHERE pid = ?" + condition,
    [query[-1]],
    -1
    )
    views  = db.query("SELECT SUM(views) FROM video WHERE pid = ?", [query[-1]])[0]

    if target is None:
        return redirect("/account")

    if views is None:
        views = 0

    return render_template(
    "page.html",
    account = account,
    target = target,
    token = token,
    videos = videos,
    views = views,
    error = error
    )

def edit(query: list[str], account: dict):
    """ edit account """

    del query
    token = get_token()

    if account is None:
        return redirect("/")

    form = get_form([
        ("type",     str),
        ("token",    str),
        ("username", str),
        ("oldpaswd", str),
        ("newpaswd", str),
        ("picture",  "FILE")
        ])

    if token != form["token"]:
        set_flash(["CSRF", "#ff0033"])
        return redirect("/account?page=" + str(account["pid"]) + "#edit")

    functions: dict = {
        "picture": picture,
        "username": username,
        "password": password,
        "delete": delete,
        }

    func = functions.get(form["type"])
    if func is None:
        set_flash(["Edited hidden form field", "#ff0033"])
        return redirect("/account?page=" + str(account["pid"]) + "#edit")

    return func(account, form)

def picture(account: dict, form: dict):
    """ change profile picutre if suitable """

    link: str = "/account?page=" + str(account["pid"])

    if form["picture"] is None:
        set_flash(["Wrong form", "#ff0033"])
        return redirect(link + "#edit")

    verdict = check_file(form["picture"], config("MAX_IMAGE_SIZE"), config("IMAGE_FILE_TYPES"))
    if not verdict[0]:
        set_flash([verdict[1], "#ff0033"])
        return redirect(link + "#edit")

    old_pfp = get_filename(account["pid"], "pfp", config("IMAGE_FILE_TYPES"))
    if old_pfp is not None:
        remove(old_pfp)

    file_type: str = form["picture"].filename.split(".")[-1]

    form["picture"].save("pfp/" + str(account["pid"]) + "." + file_type)

    return redirect(link)

def username(account: dict, form: dict):
    """ chages username if suitable """

    link: str = "/account?page=" + str(account["pid"])

    if form["username"] is None:
        set_flash(["Wrong form", "#ff0033"])
        return redirect(link + "#edit")

    verdict = check_username(form["username"])
    if not verdict[0]:
        set_flash([verdict[1], "#ff0033"])
        return redirect(link + "#edit")

    users = db.query("SELECT COUNT(pid) FROM profile WHERE username = ?", [form["username"]])

    if users[0] != 0:
        set_flash(["username is taken", "#ff0033"])
        return redirect(link + "#edit")

    db.query("UPDATE profile SET username = ? WHERE pid = ?", [form["username"], account["pid"]], 0)

    account["username"] = form["username"]
    set_account(account)

    return redirect(link)

def password(account: dict, form: dict):
    """ change password if suitable """

    link: str = "/account?page=" + str(account["pid"])

    if form["oldpaswd"] is None or form["newpaswd"] is None:
        set_flash(["Wrong form", "#ff0033"])
        return redirect(link + "#edit")

    pswd = db.query("SELECT password FROM profile WHERE pid = ?", [account["pid"]])

    if not check_password_hash(pswd[0], form["oldpaswd"]):
        set_flash(["old password does not match", "#ff0033"])
        return redirect(link + "#edit")

    verdict = check_password(form["newpaswd"])
    if not verdict[0]:
        set_flash([verdict[1], "#ff0033"])
        return redirect(link + "#edit")

    db.query("UPDATE profile SET password = ? WHERE pid = ?",
             [generate_password_hash(form["newpaswd"]), account["pid"]],
             0)

    return redirect(link)

def delete(account: dict, form: dict):
    """ deletes profile """

    del form
    clear_account()

    db.query("DELETE FROM comment WHERE pid = ?", [account["pid"]], 0)
    db.query("DELETE FROM profile WHERE pid = ?", [account["pid"]], 0)

    pfp = get_filename(account["pid"], "pfp", config("IMAGE_FILE_TYPES"))
    if pfp is not None:
        remove(pfp)

    videos: list[list[int]] = [[vid["vid"]]
    for vid in db.query("SELECT vid FROM video WHERE pid = ?", [account["pid"]], -1)
    ]

    db.query("DELETE FROM video WHERE pid = ?", [account["pid"]])
    db.multi_query("DELETE FROM comment WHERE vid = ?", videos)
    db.multi_query("DELETE FROM tag WHERE vid = ?", videos)

    for video in videos:
        remove(get_filename(video[0], "video", ["mp4"]))

    return redirect("/")
