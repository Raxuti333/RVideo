""" account settings handling """

from os import remove
from flask import redirect
from werkzeug.security import generate_password_hash, check_password_hash
from util import get_account, set_flash, get_token, clear_account, set_account
from util import get_filename, get_form, config, check_file, check_username
from util import check_password
from db import db

def handle(query: str):
    """ handle settings """

    token = get_token()
    account = get_account()
    if account is None:
        return redirect("/login")

    table = {
    "username": username, 
    "password": password, 
    "picture":  picture,
    "delete":   delete
    }

    execute = table.get(query)
    if execute is None:
        return redirect("/")

    return execute(account, token)

def picture(account: dict, token: str):
    """ change profile picutre if suitable """

    form = get_form([
    ("picture", "FILE"),
    ("token",   str),
    ("return",  str)
    ])

    link: str = form["return"]
    if link is None:
        link = "/"

    if token != form["token"]:
        set_flash(["CSRF", "#ff0033"])
        return redirect(link + "#settings")

    if form["picture"] is None:
        set_flash(["something went wrong!", "#ff0033"])
        return redirect(link + "#settings")

    verdict = check_file(form["picture"], config("MAX_IMAGE_SIZE"), config("IMAGE_FILE_TYPES"))
    if not verdict[0]:
        set_flash([verdict[1], "#ff0033"])
        return redirect(link + "#settings")

    old_pfp = get_filename(account["pid"], "pfp", config("IMAGE_FILE_TYPES"))
    if old_pfp is not None:
        remove(old_pfp)

    file_type: str = form["picture"].filename.split(".")[-1]
    form["picture"].save("pfp/" + str(account["pid"]) + "." + file_type)

    return redirect(link)

def username(account: dict, token: str):
    """ chages username if suitable """

    form = get_form([
    ("username", str),
    ("token",    str),
    ("return",   str)
    ])

    link: str = form["return"]
    if link is None:
        link = "/"

    print(link)

    if token != form["token"]:
        set_flash(["CSRF", "#ff0033"])
        return redirect(link + "#settings")

    if form["username"] is None:
        set_flash(["Wrong form", "#ff0033"])
        return redirect(link + "#settings")

    verdict = check_username(form["username"])
    if not verdict[0]:
        set_flash([verdict[1], "#ff0033"])
        return redirect(link + "#settings")

    users = db.query("SELECT COUNT(pid) FROM profile WHERE username = ?", [form["username"]])

    if users[0] != 0:
        set_flash(["username is taken", "#ff0033"])
        return redirect(link + "#settings")

    db.query("UPDATE profile SET username = ? WHERE pid = ?", [form["username"], account["pid"]], 0)

    account["username"] = form["username"]
    set_account(account)

    return redirect(link)

def password(account: dict, token: str):
    """ change password if suitable """

    form = get_form([
    ("new",      str),
    ("old",      str),
    ("token",    str),
    ("return",   str)
    ])

    link: str = form["return"]
    if link is None:
        link = "/"

    if token != form["token"]:
        set_flash(["CSRF", "#ff0033"])
        return redirect(link + "#settings")

    if form["old"] is None or form["new"] is None:
        set_flash(["Wrong form", "#ff0033"])
        return redirect(link + "#settings")

    pswd = db.query("SELECT password FROM profile WHERE pid = ?", [account["pid"]])

    if not check_password_hash(pswd[0], form["old"]):
        set_flash(["old password does not match", "#ff0033"])
        return redirect(link + "#settings")

    verdict = check_password(form["new"])
    if not verdict[0]:
        set_flash([verdict[1], "#ff0033"])
        return redirect(link + "#settings")

    db.query(
    "UPDATE profile SET password = ? WHERE pid = ?",
    [generate_password_hash(form["new"]), account["pid"]],
    0
    )

    return redirect(link)

def delete(account: dict, token: str):
    """ deletes profile """

    form = get_form([
    ("password", str),
    ("token",    str),
    ("return",   str)
    ])

    link: str = form["return"]
    if link is None:
        link = "/"

    if token != form["token"]:
        set_flash(["CSRF", "#ff0033"])
        return redirect(link + "#settings")

    pswd = db.query("SELECT password FROM profile WHERE pid = ?", [account["pid"]])
    if not check_password_hash(pswd[0], form["password"]):
        set_flash(["password does not match", "#ff0033"])
        return redirect(link + "#settings")

    clear_account()

    db.query("DELETE FROM comment WHERE pid = ?", [account["pid"]], 0)
    db.query("DELETE FROM profile WHERE pid = ?", [account["pid"]], 0)

    pfp = get_filename(account["pid"], "pfp", config("IMAGE_FILE_TYPES"))
    if pfp is not None:
        remove(pfp)

    videos: list[list[int]] = [[vid["vid"]]
    for vid in db.query("SELECT vid FROM video WHERE pid = ?", [account["pid"]], -1)
    ]

    vinfo = db.query("SELECT vid, private FROM video WHERE pid = ?", [account["pid"]], -1)

    db.query("DELETE FROM video WHERE pid = ?", [account["pid"]])
    db.multi_query("DELETE FROM comment WHERE vid = ?", videos)
    db.multi_query("DELETE FROM tag WHERE vid = ?", videos)

    for vid, private in vinfo:
        path: str = ((str(account["pid"]) + "_") if private else "") + str(vid)
        remove(get_filename(path, "video", ["mp4"]))

    return redirect("/")
