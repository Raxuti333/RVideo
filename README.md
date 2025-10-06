# RVIDEO
RVideo is a simple video sharing website!

## Features

```
✅ Signing up and Loging in
✅ Uploading videos 
✅ Commenting 
✅ Searching for videos 
✅ Advanced video search 
✅ Hastag system 
✅ Editing User profile 
✅ Video streaming 
✅ Users combined views 
✅ Editing video information 
✅ Deleting profile 
✅ Deleting video 
✅ Deleting comment 
✅ Private videos

✅ All forms use session tokens
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

read more about configuration in [.config](#config-1)

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

### Trouble shooting

If the program is crashing check your python version and see if it is at least >= 3.13.5!

## .config

The **.config** file has a simple format:

```
[KEY:TYPE DATA]
```
### Key

Supported keys are:
```
PORT - Port that the program listens to.
CHUNK_SIZE - Max stream chunks size
MAX_PFP_SIZE - Max profile picture size
MAX_FILE_SIZE - Max uploaded file size accepted by flask
INDEXES - Add db indexes
DEBUG - Add debug timing and "profiling"
PRINTS - Realtime debug info
SECRET_KEY - Secret key used by flask for secure session storage
```

### Type

Types tell the parser how to process data.

```
INTEGER - Data is cast to int
TEXT - Data is returned as is.
SIZE - Data is returned as bytes supported scalars [B, K, M, G, T, P]
BOOLEAN - Data is returned as bool keywords are [TRUE, FALSE]
```

# Preformance

## Testing

### seed.py
to generate db filled with random data run
```sh
python seed.py
```
This might take up to 10min. 

To speed up lower these variables
```py
PROFILE_COUNT = 500
VIDEOS_PER_USER = 1001
COMMENT_PER_VIDEO = 500
TAGS_PER_VIDEO = 10
TAG_MAX_LENGTH = 10
```
The defaults generate 8Gib large db

### Run/timing

#### Non-Indexed
In **.config** set:
```
[DEBUG:BOOLEAN TRUE]
[INDEXES:BOOLEAN FALSE]

// optional shows realtime timing info
[PRINTS TRUE]
```
This will collect search timings and other data displayed on program shutdown and not apply indexing to the db.

Then start the program!

#### Indexed
In **.config** set:
```
[DEBUG:BOOLEAN TRUE]
[INDEXES:BOOLEAN TRUE]

// optional shows realtime timing info
[PRINTS TRUE]
```
This will collect search timings and other data displayed on program shutdown and apply indexing to the db.

Then start the program and see the difference!

## Data

In both cases db is filled with seed.py

### Non-Indexed
copy of my debug info
```
Debug info:
max: 24.665s
avg: 0.0s
/ 2 0.005s
/static/<path:filename> 83 0.001s
/account?picture 35 0.0s
/video?stream 2172 0.0s
/video?view 2 24.268s
/account?page 2 0.112s
/account?search 1 0.012s
/?SEARCH 5 0.288s
```

### Indexed
copy of my debug info:
```
Debug info:
max: 0.701s
avg: 0.0s
/ 5 0.001s
/static/<path:filename> 260 0.001s
/account?picture 92 0.001s
/video?stream 2152 0.0s
/video?view 30 0.006s
/account?page 2 0.015s
/account?search 1 0.012s
/comment 2 0.013s
/video 2 0.028s
/?SEARCH 3 0.508s
```