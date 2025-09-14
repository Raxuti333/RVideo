#!/bin/sh

venv=../.venv/bin/activate
main=../source/main.py

# set cwd to this direcotry containing this file.
cd "$(dirname "$0")"

if [ ! -f db ]; then
    echo "creating new database to $PWD/db"
    sqlite3 db <<EOF
CREATE TABLE profile ( pid INTEGER PRIMARY KEY, username TEXT, password TEXT, date INTEGER );
CREATE TABLE video ( vid INTEGER PRIMARY KEY, pid INTEGER, name TEXT, description TEXT, date INTEGER, tags TEXT, FOREIGN KEY(pid) REFERENCES profile(pid) );
CREATE TABLE comment ( vid INTEGER, pid INTEGER, text TEXT, date INTEGER, FOREIGN KEY(vid) REFERENCES video(vid), FOREIGN KEY(pid) REFERENCES profile(pid) );
EOF
fi

if [ ! -f $venv ]; then
    echo "No venv found"
    exit 1
fi

if [ ! -f $main ]; then
    echo "No main.py found"
    exit 1
fi

mkdir -p pfp
mkdir -p video

# if moving env update these to point to the right files
source $venv
python3 $main