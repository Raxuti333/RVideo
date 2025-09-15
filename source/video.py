""" TODO """

from os import remove
from flask import render_template, redirect
from util import get_query, get_method, get_filename, get_form, check_file
from util import set_flash, get_flash, check_password, check_username, config
from util import get_session_token, send_data, set_account, get_account, get_tags
import db

def video_page():
    """ serve video page """

    token   = get_session_token()
    account = get_account()
    message = get_flash()
    query   = get_query()

    if query[0] == "view":
        return ""

    if account is None:
        return redirect("/")

    if get_method() == "POST":
        return video_upload(account, token)

    return render_template("video.html", token = token, account = account, message = message)

def video_stream():
    """ stream requested video """
    return ""

def video_upload(account: dict, token: str):
    """ create and edit video """

    form = get_form([
    ("video", "FILE"),
    ("title", str),
    ("description", str),
    ("token", str)
    ])

    if token != form["token"]:
        set_flash(["CSRF", "#ff0033"])
        return redirect("/video")

    if form["title"] is None or form["description"] is None:
        set_flash(["No title or description", "#ff0033"])
        return redirect("/video")

    if form["video"] is None:
        set_flash(["No video file", "#ff0033"])
        return redirect("/video")

    verdict = check_file(form["video"], config("MAX_FILE_SIZE"), ["mp4"])
    if not verdict[0]:
        set_flash([verdict[1], "#ff0033"])
        return redirect("/video")

    tags: str = get_tags(form["description"])

    vid: int = db.query(
    "INSERT INTO video (pid, name, description, tags, date)" 
    "VALUES(?, ?, ?, ?, unixepoch('now')) RETURNING vid", 
    [account["pid"], form["title"], form["description"], tags]
    )[0]

    file_type: str = form["video"].filename.split(".")[-1]
    hex_vid: str = hex(vid)

    form["video"].save("video/" + hex_vid + "." + file_type)

    return redirect("/video?view=" + str(vid))
