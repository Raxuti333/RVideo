""" process comment forms """

import re
from flask import redirect, abort
from util import get_form, get_account, get_token, get_vid
from db import db

EXPRESSION = re.compile(r"\d+_\d+")

def comment_form():
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

    vid = get_vid(form["vid"])

    if vid is None:
        return redirect("/")

    link: str = "/video?view=" + str(form["vid"])

    if form["cid"] is not None:
        return comment_delete(form, account, link)

    if form["comment"] is None:
        return redirect("/")

    db.query(
    "INSERT INTO comment (vid, pid, text, timestamp, date) "
    "VALUES(?, ?, ?, unixepoch('now'), date('now'))",
    [vid, account["pid"], form["comment"]],
    0
    )

    return redirect(link)

def comment_delete(form: dict, account: dict, link: str):
    """ deletes selected comment if allowed """

    db.query(
    "DELETE FROM comment WHERE cid = ? AND pid = ?",
    [form["cid"], account["pid"]],
    0
    )

    return redirect(link)
