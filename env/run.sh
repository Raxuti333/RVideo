#!/bin/sh

# set cwd to this direcotry containing this file.
cd "$(dirname "$0")"

if [ ! -f db ]; then
    echo "creating new database to $PWD/db"
    sqlite3 db <<EOF
CREATE TABLE profile ( pid INTEGER PRIMARY KEY, username TEXT, password TEXT );
CREATE TABLE video ( vid INTEGER PRIMARY KEY, pid INTEGER, name TEXT, description TEXT, date TEXT, FOREIGN KEY(pid) REFERENCES profile(pid) );
CREATE TABLE comment ( vid INTEGER, pid INTEGER, text TEXT, date TEXT, FOREIGN KEY(vid) REFERENCES video(vid), FOREIGN KEY(pid) REFERENCES profile(pid) );
EOF
fi

mkdir -p pfp

# if moving env update these to point to the right files
source ../.venv/bin/activate
python3 ../source/main.py