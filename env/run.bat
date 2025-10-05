@echo off

set venv="..\.venv\Scripts\activate.bat"
set main="..\source\main.py"

cd %~dp0

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