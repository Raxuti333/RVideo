""" process comment forms """

from flask import redirect
from util import get_form, get_account, get_token
import db

def comment_form():
    """ process comment form """

    account = get_account()
    token   = get_token()
    form    = get_form([
    ("vid", int),
    ("token", str),
    ("comment", str),
    ])

    if account is None:
        return redirect("/login")

    if form["vid"] is None or form["comment"] is None:
        return redirect("/")

    link: str = "/video?view=" + str(form["vid"])

    if token != form["token"]:
        return redirect(link)

    db.query(
    "INSERT INTO comment (vid, pid, text, date) VALUES(?, ?, ?, unixepoch('now'))",
    [form["vid"], account["pid"], form["comment"]],
    0
    )

    return redirect(link)
