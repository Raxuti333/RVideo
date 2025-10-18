""" video view page """

from flask import render_template, redirect, abort
from util import get_account, get_token, get_vid, get_query, get_flash, get_offset
from db import db

LIMIT = 25

def page(query: str):
    """ servers view page queried by user """

    account = get_account()
    token = get_token()
    message = get_flash()

    vid, pid = get_vid(query)
    if pid is not None:
        if account is None:
            return abort(403)
        if account["pid"] != pid:
            return abort(403)

    offset: int = get_offset(get_query('='))

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
    message = message,
    offset = offset
    )
