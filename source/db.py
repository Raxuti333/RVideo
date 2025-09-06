import sqlite3

def query(sql: str, params = [], count = 1):
    db = sqlite3.connect("db")
    db.row_factory = sqlite3.Row

    v = db.execute(sql, params).fetchmany(count)
    db.commit()

    db.close()
    return v