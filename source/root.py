""" Landing page processing i.e video search functions """

import re
from flask import render_template
from util import get_session_token, get_account, get_query
import db

def root_page() -> str:
    """ service function for landing page """

    token   = get_session_token()
    account = get_account()

    condition = search(get_query("&"))

    videos = db.query("SELECT vid, name FROM video " + condition[0], condition[1], 20)

    return render_template("root.html", token=token, account=account, videos = videos)

def search(query: list[str]) -> tuple[str, list]:
    """ generate sql search condition from query """

    if query[0] is "":
        return ("", [])

    params = []
    sql: str = "WHERE"

    after: bool = False

    # Generate sql query with parameters
    for m in query:
        p = m.split("=")

        if len(p) != 2 or p[-1] == "":
            continue

        match(p[0]):
            case "DATE":
                if re.match(r"^\d{4}-\d{2}-\d{2}$", p[1]) is not None:
                    sql += f" date - unixepoch('{p[1]}')"
                    if after:
                        sql += " > 0"
                    else:
                        sql += " < 0"
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
                        sql += f" pid = {u["pid"]} OR"
                    sql = sql[:len(sql) - 2] + " AND"
                else: sql += " pid = 0 AND"
            case "SEARCH":
                for x in p[1].split(" "):
                    params.append("%"+x+"%")
                    sql += " name LIKE ? OR"
                sql = sql[:len(sql) - 2] + "AND"
            case "TAGS":
                for x in p[1].split("%23"):
                    if x == "":
                        continue
                    params.append("#" + x.replace(" ", ""))
                    sql += " instr(tags, ?) > 0 OR"
                sql = sql[:len(sql) - 2] + "AND"
            case _:
                pass

    sql = sql[:len(sql) - 4]

    return (sql, params)
