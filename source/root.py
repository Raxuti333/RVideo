""" Landing page processing and video search functions """

import re
from flask import render_template
from util import get_token, get_account, get_query
from db import db

LIMIT = 24
EXPRESSION = re.compile(r"^\d{4}-\d{2}-\d{2}$")

def root_page() -> str:
    """ service function for landing page """

    token   = get_token()
    account = get_account()

    condition = search(get_query("&"), account)

    videos = db.query(
    "SELECT vid, name, private FROM video " + condition[0],
    condition[1],
    LIMIT
    )

    return render_template(
    "root.html",
    token=token,
    account=account,
    videos=videos,
    searches=condition[2]
    )

def search(query: list[str], account: dict) -> tuple[str, list, dict]:
    """ generate sql search condition from query """

    searched: dict = {}
    pid: int = account["pid"] if account is not None else -1

    if query[0] == "":
        return ("WHERE private = 0 OR pid = ?", [pid], searched)

    params = [pid]
    sql: str = "WHERE (private = 0 OR pid = ?) AND"

    page = 0
    after: bool = False
    date: bool = False

    for m in query:
        p = m.split("=")

        if len(p) != 2 or p[-1] == "":
            continue

        match(p[0]):
            case "DATE":
                if EXPRESSION.match(p[1]) is not None:
                    sql += f" timestamp - unixepoch('{p[1]}')"
                    sql += " > 0" if after else " < 0"
                    searched["DATE"] = p[1]
                else: sql += " 1"
                sql += " AND"
                date = True
            case "AFTER":
                if p[1] == "on":
                    after = True
                    searched["AFTER"] = "checked"
            case "USERS":
                users = db.query(
                    "SELECT pid FROM profile WHERE LOWER(username) LIKE LOWER(?)",
                    [p[1] + "%"],
                    10
                    )
                if users != []:
                    searched["USERS"] = p[1]
                    for u in users:
                        sql += f" pid = {u['pid']} OR"
                    sql = sql[:len(sql) - 2] + " AND"
                else: sql += " pid = 0 AND"
            case "SEARCH":
                search_query: str = ""
                for x in p[1].split("+"):
                    if x == "":
                        continue
                    params.append("%"+x+"%")
                    sql += " name LIKE ? OR"
                    search_query += x + " "
                searched["SEARCH"] = search_query
                sql = sql[:-2] + "AND"
            case "TAGS":
                searched["TAGS"] = p[1].replace("%23", "#")
                sql += search_tags(p[1].split("%23"))
            case "PAGE":
                if p[1].isdigit():
                    searched["PAGE"] = p[1]
                    page = int(p[1])
            case _:
                pass

    sql = sql[:-4]
    sql += search_order(date, after)
    sql += f" LIMIT { LIMIT } OFFSET { page * LIMIT }"

    return (sql, params, searched)

def search_order(date: bool, after: bool) -> str:
    """ create timestamp order condition """
    if not date:
        return ""
    sql: str = " ORDER BY timestamp "
    if after:
        sql += "ASC"
    else:
        sql += "DESC"
    return sql

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

    return "".join([f" vid = { vid } OR" for vid in vids])[:-2] + "AND"
