""" Landing page processing and video search functions """

import re
from flask import render_template
from util import get_token, get_account, get_query
from db import db

EXPRESSION = re.compile(r"^\d{4}-\d{2}-\d{2}$")

def root_page() -> str:
    """ service function for landing page """

    token   = get_token()
    account = get_account()

    condition = search(get_query("&"), account)

    videos = db.query("SELECT vid, name, private FROM video " + condition[0], condition[1], 20)

    return render_template("root.html", token=token, account=account, videos = videos)

def search(query: list[str], account: dict) -> tuple[str, list]:
    """ generate sql search condition from query """

    pid: int = account["pid"] if account is not None else -1

    if query[0] == "":
        return ("WHERE private = 0 OR pid = ?", [pid])

    params = [pid]
    sql: str = "WHERE (private = 0 OR pid = ?) AND"

    after: bool = False

    for m in query:
        p = m.split("=")

        if len(p) != 2 or p[-1] == "":
            continue

        match(p[0]):
            case "DATE":
                if EXPRESSION.match(p[1]) is not None:
                    sql += f" timestamp - unixepoch('{p[1]}')"
                    sql += " > 0" if after else " < 0"
                else: sql += " 1"
                sql += " AND"
            case "AFTER":
                if p[1] == "on":
                    after = True
            case "USERS":
                users = db.query(
                    "SELECT pid FROM profile WHERE LOWER(username) LIKE LOWER(?)",
                    [p[1] + "%"],
                    10
                    )
                if users != []:
                    for u in users:
                        sql += f" pid = {u['pid']} OR"
                    sql = sql[:len(sql) - 2] + " AND"
                else: sql += " pid = 0 AND"
            case "SEARCH":
                for x in p[1].split(" "):
                    params.append("%"+x+"%")
                    sql += " name LIKE ? OR"
                sql = sql[:len(sql) - 2] + "AND"
            case "TAGS":
                sql += search_tags(p[1].split("%23"))
            case _:
                pass

    sql = sql[:len(sql) - 4]

    return (sql, params)

def search_tags(tags: list[str]) -> str:
    """ return search condition for tags """
    params: list[str] = []
    sql: str = "SELECT vid FROM tag WHERE"
    for tag in tags:
        if tag == "":
            continue
        if tag[-1] == '+':
            tag = tag[:len(tag) - 1]
        params.append("#" + tag)
        sql += " instr(text, ?) > 0 OR"
    sql = sql[:len(sql) - 2]

    vids = [vid["vid"] for vid in db.query(sql, params, -1)]
    vids = list(dict.fromkeys(vids))

    if not vids:
        return ""

    sql = ""
    for vid in vids:
        sql += f" vid = { vid } OR"
    sql = sql[:len(sql) - 2]
    sql += " AND"

    return sql
