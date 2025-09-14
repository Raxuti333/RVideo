""" TODO """

from flask import render_template, redirect
from util import get_query, get_method, get_filename, get_form, get_account, send_data, get_session_token
import db

from sqlite3 import Row, Cursor

def account_page():
    """ account page """

    query = get_query()

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

    accounts: Cursor = db.query(
        "SELECT pid, username FROM profile " + 
        condition[select],
        [query[-1] + "%"] if select else [],
        5*5)

    return render_template("account_search.html", account = account, accounts = accounts)

def account_profile(query: list[str], account: dict | None):
    """ TODO """

    token = get_session_token()
    target = db.query("SELECT pid, username FROM profile WHERE pid = ?", [query[-1]])

    return render_template("account.html", account = account, target = target, token = token)

def account_picture(query: list[str]):
    """ serve account picture  """

    mimetype: dict[str, str] = {
        "png": "image/png", 
        "jpg": "image/jpeg",
        "ico": "image/vnd.microsoft.icon",
        "bmp": "image/bmp"
        }

    path = get_filename(query[-1], "pfp", ["png", "jpg", "ico", "bmp"])
    if path is None:
        return redirect("/static/no-pfp.png")

    return send_data(path, mimetype[path.split(".")[-1]])

def account_edit(account: dict):
    """ edit account """

    if account is None:
        return redirect("/")

    form = get_form([
        ("username", str),
        ("oldpaswd", str),
        ("newpaswd", str),
        ("picture",  "FILE")
        ])

    return redirect("/account?page=" + account["pid"])
