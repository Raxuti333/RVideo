""" Landing page processing and video search functions """

from flask import render_template
from util import get_token, get_account, get_query, url_parser, sql_date, sql_order
from db import db

LIMIT = 24

def page():
    """ service function for landing page """

    token   = get_token()
    account = get_account()

    sql, params, terms = search(get_query("&"), account)

    videos = db.query(sql, params, LIMIT)

    return render_template(
    "root.html",
    token = token,
    account = account,
    videos = videos,
    terms = terms
    )

def search(query: list[str], account: dict) -> tuple[str, list, dict]:
    """ generate sql search condition from query """

    terms: dict = {}
    pid: int = account["pid"] if account is not None else -1

    params = [pid]
    sql: str = "SELECT vid, name, private FROM video WHERE (private = 0 OR pid = ?)"

    condition: str = ""

    offset = 0
    after: bool = False
    date: bool = False

    for m in query:
        p = m.split("=")

        if len(p) != 2 or p[-1] == "":
            continue

        p[1] = url_parser(p[1].replace('+', ' '))
        terms[p[0].lower()] = p[1]

        match(p[0]):
            case "DATE":
                condition += sql_date(p[1], after)
                date = True
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
                        condition += f" pid = {u['pid']} OR"
                    condition = condition[:len(condition) - 2] + " AND"
                else: sql += " pid = 0 AND"
            case "SEARCH":
                search_query: str = ""
                for x in p[1].split(" "):
                    if x == "":
                        continue
                    params.append("%"+x+"%")
                    condition += " name LIKE ? OR"
                    search_query += x + " "
                condition = condition[:-2] + "AND"
            case "TAGS":
                condition += search_tags(p[1].split('#'))
            case "PAGE":
                if p[1].isdigit():
                    offset = int(p[1])
            case _:
                pass

    condition = condition[:-4]
    if condition != "":
        sql += "AND (" + condition + ")"
    sql += sql_order(date, after)
    sql += f" LIMIT { LIMIT } OFFSET { offset * LIMIT }"

    print(sql)
    return (sql, params, terms)

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

    vids = [vid["vid"] for vid in db.query(sql, params, 100)]
    vids = list(dict.fromkeys(vids))

    if not vids:
        return ""

    return "".join([f" vid = { vid } OR" for vid in vids])[:-2] + "AND"
