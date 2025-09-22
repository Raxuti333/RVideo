# RVIDEO
RVideo is a simple video sharing website!

## Features

```
Signing up and Loging in ✅
Uploading videos ✅
Commenting ✅
Searching for videos ✅
Advanced video search ✅
Hastag system ✅
Editing User profile ✅
Video streaming ✅
Users combined views ❌
Editing video information ❌
Deleting profile ❌
Deleting video ❌
Deleting comment ❌

All forms use session tokens ✅
```

✅ - feature is complete

❌ - feature is incomplete

## Running

### download

#### Git

to download the source files run:
```sh
git clone https://github.com/Raxuti333/RVideo.git
```

#### Zip

if you don't have git installed

##### Linux

run to install the source zip from github
```sh
curl -o Rvideo.zip "https://codeload.github.com/Raxuti333/RVideo/zip/refs/heads/master"
unzip Rvideo.zip
```

##### Windows 10/11

open cmd and run:
```sh
curl -o Rvideo.zip "https://codeload.github.com/Raxuti333/RVideo/zip/refs/heads/master"
tar -xf Rvideo.zip
```

### Python

#### version
Rvideo is developed with CPython-3.13.5 and uses typehints.

If you are using using python version <= 3.10 you may have problems with typehints.

To check your python version:
```sh
python --version
```

#### virtual environement

move into the project root and run:
```sh
python -m venv .venv
```

#### dependencies

the project is dependent **flask** and **sqlite3**

The automatic starting script requires [**sqlite3 cli**](https://sqlite.org/cli.html)

##### Linux
to install flask **flask** move into project root and run:
```sh
source .venv/bin/activate
pip install Flask
```
Also check that you have sqlite3 installed. Its rather unlikely that you don't have it.

Also check that you have **sqlite cli**.
easy way to check is to run:
```sh
sqlite3 --version
```

if the command fails install **sqlite3 cli** from your package manager or from https://sqlite.org/download.html under Precompiled Binaries for Linux

##### Windows

to install flask flask move into project root and run:
```bat
.venv\Scripts\actiavte.bat
pip install Flask
```

Also check that you have **sqlite cli**.
easy way to check is to run:
```sh
sqlite3.exe --version
```

you can download sqlite3.exe from https://sqlite.org/download.html under Precompiled Binaries for Windows

if you don't want to add sqlite3.exe to your **PATH** you can also set the exe in the **env** folder

### Config

read more about configuration in [.config](#.config)

open env/.config in a text editor.

In **.config** replace the old secret key with a new one.
```
[SECRET_KEY:TEXT <secret key>]
```

To generate a new secret key run:
```py
python
>>> from secrets import token_hex
>>> token_hex(16)
'26e021e2ec284d6276011e726a42efea'
```

### Run

#### Linux

run:
```sh
env/run.sh
```
This will automatically create the **db** as well.

if you wish to run the program "manually" read the contents of **run.sh**

you can now access the website from address "http://127.0.0.1:8080"
if you have changed the port in the **.conf** use it instead of the 8080

#### Windows

```sh
env\run.bat
```
This will automatically create the **db** as well.

if you wish to run the program "manually" read the contents of **run.sh**

you can now access the website from address "http://127.0.0.1:8080"
if you have changed the port in the **.conf** use it instead of the 8080
