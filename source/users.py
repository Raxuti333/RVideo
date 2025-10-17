""" serve and handle users.html """

import re
from flask import render_template
from util import get_query, get_account, url_parser
from db import db

LIMIT = 25
EXPRESSION = re.compile(r"^\d{4}-\d{2}-\d{2}$")

def page():
    """ serve users.html """

    account = get_account()

    sql, params, terms = user_search()
    users = db.query(sql, params, LIMIT)

    return render_template(
    "users.html",
    users = users,
    terms = terms,
    account = account
    )

def user_search() -> tuple[str, list, dict]:
    """ generate sql query from search terms """

    offset = 0
    date = False
    after = False
    params = []
    sql: str = "SELECT pid, username FROM profile WHERE "
    terms = {}

    for m in get_query("&"):
        p = m.split("=")

        if len(p) != 2:
            continue

        p[1] = url_parser(p[1].replace('+', ' '))
        terms[p[0].lower()] = p[1]

        match(p[0]):
            case "SEARCH":
                params.append(p[1] + "%")
                sql += "username LIKE ? AND"
            case "DATE":
                if EXPRESSION.match(p[1]) is not None:
                    sql += f" timestamp - unixepoch('{p[1]}')"
                    sql += " > 0" if after else " < 0"
                else: sql += " 1"
                sql += " AND"
                date = True
            case "AFTER":
                if p[1] == "on":
                    after = True
            case "PAGE":
                if p[1].isdigit():
                    offset = int(p[1])

    sql = sql[:-4]
    sql += order(date, after)
    sql += f" LIMIT { LIMIT } OFFSET { offset * LIMIT }"

    return (sql, params, terms)

def order(date: bool, after: bool) -> str:
    """ create timestamp order condition """
    if not date:
        return ""
    sql: str = " ORDER BY timestamp "
    if after:
        sql += "ASC"
    else:
        sql += "DESC"
    return sql
