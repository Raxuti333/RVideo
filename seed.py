from os import remove
from random import randint, choices
from datetime import datetime
from string import ascii_lowercase, ascii_uppercase
import sqlite3

remove("env/db")
db = sqlite3.connect("env/db")

with open("env/db.sql", encoding="utf-8") as sql:
    db.executescript(sql.read())

#uncomment to build with indexes can be activated later as well
#with open("env/index.sql", encoding="utf-8") as sql:
#    db.executescript(sql.read())

PROFILE_COUNT = 500
VIDEOS_PER_USER = 1001
COMMENT_PER_VIDEO = 500
TAGS_PER_VIDEO = 10
TAG_MAX_LENGTH = 10

vid = 1
for pid in range(1, PROFILE_COUNT):
    db.execute("INSERT INTO profile (username, timestamp, date) VALUES (?, 0, 1970-01-01)", ["user" + str(pid)])

    video: list[list[str]] = []
    comment: list[list[str]] = []
    tag: list[list[str]] = []

    for i in range(1, VIDEOS_PER_USER):
        timestamp: int = randint(0, 4294967295)
        date: str = datetime.fromtimestamp(timestamp).date()

        video.append([pid, "video" + str(i), timestamp, str(date)])

        for cid in range(1, COMMENT_PER_VIDEO):
            comment.append([vid, pid, "comment" + str(cid), timestamp])

        for tid in range(1, TAGS_PER_VIDEO):
            text: str = "#" + ''.join(choices(ascii_lowercase + ascii_uppercase, k=randint(1, TAG_MAX_LENGTH)))
            tag.append([vid, text])
        vid += 1

    db.executemany("INSERT INTO video (pid, private, name, timestamp, date, views) VALUES (?, 0, ?, ?, ?, 0)", video)
    db.executemany("INSERT INTO comment (vid, pid, text, timestamp) VALUES (?, ?, ?, ?)", comment)
    db.executemany("INSERT INTO tag (vid, text) VALUES (?, ?)", tag)
    print(pid, "/", PROFILE_COUNT)


db.commit()
db.close()
