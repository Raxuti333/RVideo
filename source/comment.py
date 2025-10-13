""" process comment forms """

from flask import redirect, abort
from util import get_form, get_account, get_token, get_vid
from db import db

def handle():
    """ process comment form """

    account = get_account()
    token   = get_token()
    form    = get_form([
    ("cid", int),
    ("vid", str),
    ("token", str),
    ("comment", str),
    ])

    if token != form["token"]:
        return abort(400)

    if account is None:
        return redirect("/login")

    vid = get_vid(form["vid"])[0]

    if vid is None:
        return redirect("/")

    link: str = "/view/" + str(form["vid"])

    if form["cid"] is not None:
        return delete(form, account, link)

    if form["comment"] is None or form["comment"] == "":
        return redirect("/")

    db.query(
    "INSERT INTO comment (vid, pid, text, timestamp, date) "
    "VALUES(?, ?, ?, unixepoch('now'), date('now'))",
    [vid, account["pid"], form["comment"]],
    0
    )

    return redirect(link)

def delete(form: dict, account: dict, link: str):
    """ deletes selected comment if allowed """

    db.query(
    "DELETE FROM comment WHERE cid = ? AND pid = ?",
    [form["cid"], account["pid"]],
    0
    )

    return redirect(link)
