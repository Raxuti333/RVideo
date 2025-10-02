""" account.html and accounts_search.html rendering and form handling """

from os import remove
from flask import render_template, redirect
from werkzeug.security import generate_password_hash, check_password_hash
from util import get_query, get_method, get_filename, get_form, check_file
from util import set_flash, get_flash, check_password, check_username, config
from util import get_token, send_data, set_account, get_account, clear_account
from db import db

IMAGE_FILE_TYPES: list[str] = ["png", "jpg", "ico", "bmp"]

def account_page():
    """ account page and sub resource routing """

    query = get_query("=")
    account = get_account()

    if get_method() == "POST":
        return account_edit(account)

    if query[0] == "picture":
        return account_picture(query)

    if query[0] == "page":
        return account_profile(query, account)

    condition: dict = {
        True: "WHERE LOWER(username) LIKE LOWER(?)",
        False: "ORDER BY pid DESC"
        }

    select: bool = query[0] == "search"

    accounts = db.query(
        "SELECT pid, username FROM profile " + 
        condition[select],
        [query[-1] + "%"] if select else [],
        5*5)

    return render_template("account_search.html", account = account, accounts = accounts)

def account_profile(query: list[str], account: dict | None):
    """ profile page """

    token = get_token()
    error = get_flash()
    target = db.query("SELECT pid, username, date FROM profile WHERE pid = ?", [query[-1]])
    videos = db.query("SELECT vid, name, pid FROM video WHERE pid = ?", [query[-1]], -1)
    views  = db.query("SELECT SUM(views) FROM video WHERE pid = ?", [query[-1]])[0]

    if target is None:
        return redirect("/account")

    if views is None:
        views = 0

    return render_template("account.html",
    account = account,
    target = target,
    token = token,
    videos = videos,
    views = views,
    error = error
    )

def account_picture(query: list[str]):
    """ fetch account picture """

    mimetype: dict[str, str] = {
        "png": "image/png", 
        "jpg": "image/jpeg",
        "ico": "image/vnd.microsoft.icon",
        "bmp": "image/bmp"
        }

    path = get_filename(query[-1], "pfp", IMAGE_FILE_TYPES)
    if path is None:
        return redirect("/static/no-pfp.png")

    return send_data(path, mimetype[path.split(".")[-1]])

def account_edit(account: dict):
    """ edit account """

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
        "picture": edit_picture,
        "username": edit_username,
        "password": edit_password,
        "delete": delete_profile,
        }

    func = functions.get(form["type"])
    if func is None:
        set_flash(["Edited hidden form field", "#ff0033"])
        return redirect("/account?page=" + str(account["pid"]) + "#edit")

    return func(account, form)

def edit_picture(account: dict, form: dict):
    """ change profile picutre if suitable """

    link: str = "/account?page=" + str(account["pid"])

    if form["picture"] is None:
        set_flash(["Wrong form", "#ff0033"])
        return redirect(link + "#edit")

    verdict = check_file(form["picture"], config("MAX_PFP_SIZE"), IMAGE_FILE_TYPES)
    if not verdict[0]:
        set_flash([verdict[1], "#ff0033"])
        return redirect(link + "#edit")

    old_pfp = get_filename(account["pid"], "pfp", IMAGE_FILE_TYPES)
    if old_pfp is not None:
        remove(old_pfp)

    file_type: str = form["picture"].filename.split(".")[-1]
    hex_pid: str = hex(account["pid"])

    form["picture"].save("pfp/" + hex_pid + "." + file_type)

    return redirect(link)

def edit_username(account: dict, form: dict):
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

def edit_password(account: dict, form: dict):
    """ change password if suitable """

    link: str = "/account?page=" + str(account["pid"])

    if form["oldpaswd"] is None or form["newpaswd"] is None:
        set_flash(["Wrong form", "#ff0033"])
        return redirect(link + "#edit")

    password = db.query("SELECT password FROM profile WHERE pid = ?", [account["pid"]])

    if not check_password_hash(password[0], form["oldpaswd"]):
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

def delete_profile(account: dict, form: dict):
    """ deletes profile """

    del form
    clear_account()

    db.query("DELETE FROM comment WHERE pid = ?", [account["pid"]], 0)
    db.query("DELETE FROM profile WHERE pid = ?", [account["pid"]], 0)

    pfp = get_filename(account["pid"], "pfp", IMAGE_FILE_TYPES)
    if pfp is not None:
        remove(pfp)

    videos: list[int] = db.query("SELECT vid FROM video WHERE pid = ?", [account["pid"]], -1)

    for video in videos:
        db.query("DELETE FROM video WHERE vid = ?", [video["vid"]], 0)
        db.query("DELETE FROM comment WHERE vid = ?", [video["vid"]], 0)
        remove(get_filename(video["vid"], "video", ["mp4"]))

    return redirect("/")
