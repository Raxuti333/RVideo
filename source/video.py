""" server and handle video pages and forms """

from os import remove, SEEK_SET, SEEK_END
from flask import render_template, redirect, abort, Response
from util import get_query, get_method, get_filename, get_form
from util import set_flash, get_flash, config, get_range
from util import get_token, get_account, get_tags, check_video
from db import db

def video_page():
    """ serve video page """

    token   = get_token()
    account = get_account()
    message = get_flash()
    query   = get_query("=")

    if query[0] == "view":
        return video_view(account, token, query)

    if query[0] == "stream":
        return video_stream(query)

    if account is None:
        return redirect("/")

    if get_method() == "POST":
        return video_form(account, token)

    return render_template("video.html", token = token, account = account, message = message)

def video_view(account: dict, token: str, query: list[str]):
    """ servers view page queried by user """
    vid: str = query[-1]

    video = db.query(
    "UPDATE video SET views = views + 1 WHERE vid = ? "
    "RETURNING name, description, pid, views, date",
    [vid]
    )

    if video is None:
        return redirect("/")

    target = db.query("SELECT pid, username FROM profile WHERE pid = ?", [video["pid"]])
    comments = db.query("SELECT cid, pid, text FROM comment WHERE vid = ?", [vid], -1)

    return render_template("view.html",
                           token = token,
                           account = account,
                           video = video,
                           target = target,
                           comments = comments,
                           vid = vid
                          )

def video_stream(query: str):
    """ 
    stream requested video 
    TODO optimize
    """

    path: str = get_filename(query[-1], "video", ["mp4"])
    if path is None:
        return abort(404)

    start: int = get_range()

    with open(path, "rb") as video:
        chunk_size: int = config("CHUNK_SIZE")

        video.seek(0, SEEK_END)
        size: int = video.tell()

        end: int = min(start + chunk_size, size - 1)

        video.seek(start, SEEK_SET)
        chunk: bytes = video.read(chunk_size)

    headers = {
        "Content-Range": f"bytes {start}-{end}/{size}",
        "Accept-Ranges": "bytes",
        "Content-Length": end - start + 1,
        "Content-Type": "video/mp4",
    }

    return Response(chunk, 206, headers)

def video_form(account: dict, token: str):
    """ selector function """

    form    = get_form([
    ("video", "FILE"),
    ("title", str),
    ("description", str),
    ("token", str),

    ("vid", int),
    ("select", str)
    ])

    if token != form["token"]:
        set_flash(["CSRF", "#ff0033"])
        return redirect("/video")

    if form["vid"] is None:
        return video_upload(account, form)

    edit: dict[int] = {"title": title, "description": description, "delete": delete}

    editing = edit.get(form["select"])
    if editing is None:
        return redirect("/")

    return editing(account, form)

def title(account: dict, form: dict):
    """ change title """

    link: str = "/video?view=" + str(form["vid"])

    if form["title"] is None:
        set_flash(["title is empty", "#ff0033"])
        return redirect(link)

    db.query("UPDATE video SET name = ? WHERE vid = ? AND pid = ?",
    [form["title"], form["vid"], account["pid"]],
    0)

    return redirect(link)

def description(account: dict, form: dict):
    """ change description redo tags 
        TODO update tags
    """
    link: str = "/video?view=" + str(form["vid"])

    if form["description"] is None:
        set_flash(["description is empty", "#ff0033"])
        return redirect(link)

    db.query("UPDATE video SET description = ? WHERE vid = ? AND pid = ?",
    [form["description"], form["vid"], account["pid"]],
    0)

    return redirect(link)

def delete(account: dict, form: dict):
    """ remove video """

    path: str = get_filename(form["vid"], "video", ["mp4"])
    if path is None:
        return redirect("/")

    vid: int = db.query("DELETE FROM video WHERE vid = ? AND pid = ? RETURNING vid",
    [form["vid"], account["pid"]])

    if vid is None:
        return redirect("/video?view=" + str(form["vid"]))

    db.query("DELETE FROM comment WHERE vid = ?", [form["vid"]], 0)

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

    tags: str = get_tags(form["description"])

    vid: int = db.query(
    "INSERT INTO video (pid, name, description, tags, views, timestamp, date)" 
    "VALUES(?, ?, ?, ?, 0, unixepoch('now'), date('now')) RETURNING vid", 
    [account["pid"], form["title"], form["description"], tags]
    )[0]

    file_type: str = form["video"].filename.split(".")[-1]
    hex_vid: str = hex(vid)

    form["video"].save("video/" + hex_vid + "." + file_type)

    return redirect("/video?view=" + str(vid))
