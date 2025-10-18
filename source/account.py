""" html rendering and form handling """

from flask import render_template, redirect
from util import get_query, get_offset, get_account, get_flash, get_token
from db import db

LIMIT = 14

def page(pid: int):
    """ account page and sub resource routing """

    account = get_account()
    token   = get_token()
    offset  = get_offset(get_query('='))
    message = get_flash()

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

    info = db.query("SELECT COUNT(vid), SUM(views) FROM video WHERE pid = ?", [pid])

    return render_template(
    "page.html",
    account = account,
    target = target,
    videos = videos,
    token = token,
    views = 0 if info[1] is None else info[1],
    count = info[0],
    message = message,
    offset = offset
    )
