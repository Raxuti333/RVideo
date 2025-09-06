import sqlite3
from parse import config

def query(sql: str, params = []):
    db = sqlite3.connect("db")
    db.row_factory = sqlite3.Row

    v = db.execute(sql, params)
    db.commit()

    db.close()
    return v