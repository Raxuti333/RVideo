""" server and handle video pages and forms """

from os import remove
from flask import render_template, redirect
from util import get_method, get_filename, get_form
from util import set_flash, get_flash, config, get_vid
from util import get_token, get_account, get_tags, check_video
from db import db

def video_page():
    """ serve video page """

    token   = get_token()
    account = get_account()
    message = get_flash()

    if account is None:
        return redirect("/")

    if get_method() == "POST":
        return video_form(account, token)

    return render_template("video.html", token = token, account = account, message = message)

def video_form(account: dict, token: str):
    """ selector function """

    form    = get_form([
    ("video", "FILE"),
    ("title", str),
    ("description", str),
    ("private", str),
    ("token", str),

    ("vid", str),
    ("select", str)
    ])

    if token != form["token"]:
        set_flash(["CSRF", "#ff0033"])
        return redirect("/video")

    if form["vid"] is None:
        return video_upload(account, form)

    if get_vid(form["vid"])[0] is None:
        return redirect("/")

    edit: dict[int] = {"title": title, "description": description, "delete": delete}

    editing = edit.get(form["select"])
    if editing is None:
        return redirect("/")

    return editing(account, form)

def title(account: dict, form: dict):
    """ change title """

    link: str = "/view/" + str(form["vid"])

    vid = get_vid(form["vid"])[0]

    if form["title"] is None:
        set_flash(["title is empty", "#ff0033"])
        return redirect(link)

    db.query("UPDATE video SET name = ? WHERE vid = ? AND pid = ?",
    [form["title"], vid, account["pid"]],
    0)

    return redirect(link)

def description(account: dict, form: dict):
    """ change description redo tags 
        TODO update tags
    """
    link: str = "/view/" + str(form["vid"])

    vid = get_vid(form["vid"])[0]

    if form["description"] is None:
        set_flash(["description is empty", "#ff0033"])
        return redirect(link)

    value = db.query("UPDATE video SET description = ? WHERE vid = ? AND pid = ? RETURNING vid",
    [form["description"], vid, account["pid"]]
    )

    if value is None:
        return redirect(link)

    db.query("DELETE FROM tag WHERE vid = ?", [vid], 0)
    queries: list[tuple[int, str]] = []
    tags: list[str] = get_tags(form["description"])
    for tag in tags:
        queries.append((vid, tag))
    db.multi_query("INSERT INTO tag (vid, text) VALUES(?, ?)", queries)

    return redirect(link)

def delete(account: dict, form: dict):
    """ remove video """

    vid = get_vid(form["vid"])[0]

    path: str = get_filename(form["vid"], "video", ["mp4"])
    if path is None:
        return redirect("/")

    vid: int = db.query("DELETE FROM video WHERE vid = ? AND pid = ? RETURNING vid",
    [vid, account["pid"]])

    if vid is None:
        return redirect("/view/" + str(form["vid"]))

    db.query("DELETE FROM comment WHERE vid = ?", [vid["vid"]], 0)
    db.query("DELETE FROM tag WHERE vid = ?", [vid["vid"]], 0)

    remove(path)

    return redirect("/account?page=" + str(account["pid"]))

def video_upload(account: dict, form: dict):
    """ create and edit video """

    if form["title"] is None or form["description"] is None:
        set_flash(["No title or description", "#ff0033"])
        return redirect("/video")

    if form["video"] is None:
        set_flash(["No video file", "#ff0033"])
        return redirect("/video")

    verdict = check_video(form["video"], config("MAX_FILE_SIZE"))
    if not verdict[0]:
        set_flash([verdict[1], "#ff0033"])
        return redirect("/video")

    private: bool = form["private"] == "on"

    vid: int = db.query(
    "INSERT INTO video (pid, name, description, private, views, timestamp, date)" 
    "VALUES(?, ?, ?, ?, 0, unixepoch('now'), date('now')) RETURNING vid", 
    [account["pid"], form["title"], form["description"], private]
    )[0]

    queries: list[tuple[int, str]] = []
    tags: list[str] = get_tags(form["description"])
    for tag in tags:
        queries.append((vid, tag))

    db.multi_query("INSERT INTO tag (vid, text) VALUES(?, ?)", queries)

    path: str = str(vid)
    if private:
        path = str(account["pid"]) + "_" + path

    file_type: str = form["video"].filename.split(".")[-1]

    form["video"].save("video/" + path + "." + file_type)

    return redirect("/view/" + path)
