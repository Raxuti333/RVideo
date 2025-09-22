""" database query function """

import sqlite3

def query(sql: str, params: list = None, count: int = 1) -> sqlite3.Row | sqlite3.Cursor | None:
    """ query data from sqlite3 db\n
    count = 1: fetchone()\n
    count = -1: fetchall()\n
    count = n: fetchmany(n)\n
    count = 0: None
    """
    db = sqlite3.connect("db")
    db.row_factory = sqlite3.Row

    cursor = db.execute(sql, params)

    match(count):
        case 1: result = cursor.fetchone()
        case -1: result = cursor.fetchall()
        case 0: result = None
        case _: result = cursor.fetchmany(count)

    db.commit()
    db.close()

    return result
