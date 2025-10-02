""" database query function """

import sqlite3
from threading import Lock

class Database:
    """ Hold database information """

    def __init__(self):
        self.db = sqlite3.connect("db", check_same_thread=False)
        self.db.row_factory = sqlite3.Row
        self.lock = Lock()

    def __del__(self):
        self.db.close()

    def query(self, sql: str, params: list = None, count: int = 1):
        """ query data from sqlite3 db\n
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

db: Database = Database()
