
""" video view page """

from flask import render_template, redirect, abort
from util import get_account, get_token, get_vid, get_query
from db import db

LIMIT = 25

def view_page(query: str):
    """ servers view page queried by user """

    account = get_account()
    token   = get_token()

    vid, pid = get_vid(query)
    if pid is not None:
        if account is None:
            return abort(403)
        if account["pid"] != pid:
            return abort(403)

    offset: int = get_offset()

    video = db.query(
    "UPDATE video SET views = views + 1 WHERE vid = ? "
    "RETURNING name, description, pid, views, private, date",
    [vid]
    )

    if video is None:
        return redirect("/")

    target = db.query("SELECT pid, username FROM profile WHERE pid = ?", [video["pid"]])
    comments = db.query(
    "SELECT cid, pid, text FROM comment WHERE vid = ?" +
    f" ORDER BY timestamp ASC LIMIT { LIMIT } OFFSET { offset * LIMIT }",
    [vid],
    LIMIT
    )

    return render_template(
    "view.html",
    token = token,
    account = account,
    video = video,
    target = target,
    comments = comments,
    vid = query,
    offset = {"current": offset, "next": offset + 1, "last": offset - 1}
    )

def get_offset() -> int:
    """ get offset from query """

    query = get_query("=")

    if query[0] == "offset":
        if query[-1].isdigit():
            return int(query[-1])

    return 0
