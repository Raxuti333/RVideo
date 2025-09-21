@echo off

set db="db.sql"
set venv="..\.venv\Scripts\activate.bat"
set main="..\source\main.py"

cd %~dp0

if not exist "db" (
    echo creating new database to %CD%\db
    type %db% | sqlite3.exe db
)

if not exist %venv% (
    echo No venv found
    exit /b 1
)

if not exist %main% (
    echo No main.py found
    exit /b 1
)

mkdir pfp
mkdir video

call %venv%
python %main%