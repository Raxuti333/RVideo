#!/bin/sh

db=db.sql
venv=../.venv/bin/activate
main=../source/main.py

# set cwd to this direcotry containing this file.
cd "$(dirname "$0")"

if [ ! -f db ]; then
    echo "creating new database to $PWD/db"
    cat $db | sqlite3 db
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
python $main