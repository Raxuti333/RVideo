#!/bin/bash

# set cwd to this direcotry containing this file.
cd "$(dirname "$0")"

if [ ! -f db ]; then
    echo "no database found in $PWD/db"
    echo "creating new database to $PWD/db"
    # TODO sqlite db creation
fi


# if moving env update these to point to the right files
source ../.venv/bin/activate
python3 ../source/main.py