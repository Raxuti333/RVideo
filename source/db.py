""" 
database class and query functions
"""

import re
import sqlite3
from threading import Lock
from util import config

EXPRESSION = re.compile(r"^sqlite_autoindex_profile_\d+$")

def setup(connection):
    """ 
    Checks db tables and creates them if missing.\n
    If .config INDEXES TRUE checks indexes and creates them if missing.\n
    If .config INDEXES is FALSE but db contains indexes they will be deleted.\n
    """

    with open("db.sql", encoding="utf-8") as sql:
        connection.executescript(sql.read())

    if not config("INDEXES"):
        print("removing indexes!")
        indexes = connection.execute("SELECT name FROM sqlite_master WHERE type='index'")
        for p in indexes:
            if EXPRESSION.match(p['name']) is None:
                connection.execute(f"DROP INDEX IF EXISTS { p['name'] }")
        return

    with open("index.sql", encoding="utf-8") as sql:
        print("creating indexes!")
        connection.executescript(sql.read())

class Database:
    """
    Database class exists to hold speed up db queries by removing db.connect calls.
    Instead using Locks to prevent simulatinous access.
    The class also exists to utilize pythons garbage collector to automatically call db.close 
    on program shutdown
    """

    def __init__(self):
        self.db = sqlite3.connect("db", check_same_thread=False)
        self.db.row_factory = sqlite3.Row
        self.lock = Lock()
        setup(self.db)
        self.db.commit()

    def __del__(self):
        self.db.close()

    def query(self, sql: str, params: list = None, count: int = 1):
        """ 
        query data from sqlite3 db\n
        count = 1: fetchone()\n
        count = -1: fetchall()\n
        count = n: fetchmany(n)\n
        count = 0: None
        """

        with self.lock:
            cursor = self.db.execute(sql, params)

            match(count):
                case 1: result = cursor.fetchone()
                case -1: result = cursor.fetchall()
                case 0: result = None
                case _: result = cursor.fetchmany(count)

            self.db.commit()

        return result

    def multi_query(self, sql: str, params: list[list] = None):
        """ 
        multi query data from sqlite3 db\n
        count = 1: fetchone()\n
        count = -1: fetchall()\n
        count = n: fetchmany(n)\n
        count = 0: None
        """

        with self.lock:
            self.db.executemany(sql, params)
            self.db.commit()

db: Database = Database()
