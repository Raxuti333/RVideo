""" server and handle video pages and forms """

from os import remove
from flask import render_template, redirect
from util import get_filename, get_form, get_query
from util import set_flash, get_flash, config, get_vid
from util import get_token, get_account, get_tags, check_video
from db import db

def page():
    """ serve video page """

    token = get_token()
    account = get_account()
    message = get_flash()
    query = get_query("=")

    if account is None:
        return redirect("/")

    table: dict = {"upload": upload, "edit": edit, "delete": delete }
    execute = table.get(query[0])
    if execute is not None:
        return execute(account, token)

    return render_template(
    "video.html",
    token = token,
    account = account,
    message = message
    )

def edit(account: dict, token: str):
    """ selector function """

    form = get_form([
    ("vid", str),
    ("title", str),
    ("description", str),
    ("token", str),
    ])

    link: str = "/view/" + str(form["vid"])

    if token != form["token"]:
        set_flash(["CSRF", "#ff0033"])
        return redirect("/video")

    vid = get_vid(form["vid"])[0]
    if vid is None:
        return redirect("/")

    if form["title"] is None or form["title"] == "":
        set_flash(["title is empty", "#ff0033"])
        return redirect(link + "#edit")

    if form["description"] is None:
        set_flash(["description is empty", "#ff0033"])
        return redirect(link + "#edit")

    success = db.query(
    "UPDATE video SET name = ?, description = ? WHERE vid = ? AND pid = ? RETURNING vid",
    [form["title"], form["description"], vid, account["pid"]]
    )

    if success is None:
        set_flash(["something went wrong!", "#ff0033"])
        return redirect(link + "#edit")

    db.query("DELETE FROM tag WHERE vid = ?", [vid], 0)
    queries: list[tuple[int, str]] = []
    tags: list[str] = get_tags(form["description"])
    for tag in tags:
        queries.append((vid, tag))
    db.multi_query("INSERT INTO tag (vid, text) VALUES(?, ?)", queries)

    return redirect(link)

def delete(account: dict, token: str):
    """ remove video """

    form = get_form([
    ("vid", str),
    ("token", str),
    ])

    link: str = "/view/" + str(form["vid"])

    if token != form["token"]:
        set_flash(["CSRF", "#ff0033"])
        return redirect("/video")

    vid = get_vid(form["vid"])[0]
    if vid is None:
        return redirect("/")

    path: str = get_filename(form["vid"], "video", ["mp4"])
    if path is None:
        return redirect("/")

    vid: int = db.query("DELETE FROM video WHERE vid = ? AND pid = ? RETURNING vid",
    [vid, account["pid"]])

    if vid is None:
        set_flash(["something went wrong!", "#ff0033"])
        return redirect(link + "#edit")

    db.query("DELETE FROM comment WHERE vid = ?", [vid["vid"]], 0)
    db.query("DELETE FROM tag WHERE vid = ?", [vid["vid"]], 0)

    remove(path)

    return redirect("/account/" + str(account["pid"]))

def upload(account: dict, token: str):
    """ create and edit video """

    form = get_form([
    ("video", "FILE"),
    ("title", str),
    ("description", str),
    ("private", str),
    ("token", str),
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
