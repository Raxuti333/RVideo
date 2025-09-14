""" TODO """

from flask import render_template, redirect
from util import get_query, get_method, get_filename, send_data
import db

def account_page():
    """ account page """

    query = get_query()

    if get_method() == "POST":
        return account_edit()

    if query[0] == "picture":
        return account_picture(query)

    return render_template("account.html")

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

def account_edit():
    """ edit account """
    return ""
