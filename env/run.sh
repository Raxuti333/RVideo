#!/bin/sh

# set cwd to this direcotry containing this file.
cd "$(dirname "$0")"

if [ ! -f db ]; then
    echo "creating new database to $PWD/db"
    sqlite3 db <<EOF
CREATE TABLE profile ( pid INTEGER PRIMARY KEY, username TEXT, password TEXT );
CREATE TABLE video ( vid INTEGER PRIMARY KEY, pid INTEGER, FOREIGN KEY(pid) REFERENCES profile(pid), name TEXT, description TEXT, date TEXT );
CREATE TABLE comment ( vid INTEGER, FOREIGN KEY(vid) REFERENCES video(vid), pid INTEGER, FOREIGN KEY(pid) REFERENCES profile(pid), text TEXT, date TEXT );
EOF
fi


# if moving env update these to point to the right files
source ../.venv/bin/activate
python3 ../source/main.py