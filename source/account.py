""" html rendering and form handling """

import re
from os import remove
from flask import render_template, redirect
from werkzeug.security import generate_password_hash, check_password_hash
from util import get_query, get_filename, get_form, check_file, config
from util import set_flash, check_password, check_username, clear_account
from util import get_token, set_account, get_account
from db import db

LIMIT = 20
EXPRESSION = re.compile(r"^\d{4}-\d{2}-\d{2}$")

def page(pid: int):
    """ account page and sub resource routing """

    account = get_account()
    offset = get_offset()

    target = db.query(
    "SELECT pid, username, date FROM profile WHERE pid = ?",
    [pid],
    1
    )

    if target is None:
        return redirect("/users")

    videos = db.query(
    "SELECT vid, private, name FROM video WHERE (private = 0 OR pid = ?) AND pid = ? "
    f"LIMIT { LIMIT } OFFSET { offset * LIMIT }",
    [-1 if account is None else account["pid"], pid],
    LIMIT
    )

    return render_template(
    "page.html",
    account = account,
    target = target,
    videos = videos,
    offset = offset
    )

def get_offset() -> int:
    """ get video offset """
    p = get_query("=")

    if len(p) == 2 and p[0] == "offset":
        if p[1].isdigit():
            return int(p[1])

    return 0

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

    db.query(
    "UPDATE profile SET password = ? WHERE pid = ?",
    [generate_password_hash(form["newpaswd"]), account["pid"]],
    0
    )

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
