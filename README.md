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

##### Linux
to install flask **flask** move into project root and run:
```sh
source .venv/bin/activate
pip install Flask
```

##### Windows

to install flask flask move into project root and run:
```bat
.venv\Scripts\actiavte.bat
pip install Flask
```

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

if you wish to run the program "manually" read the contents of **run.bat**

you can now access the website from address "http://127.0.0.1:8080"
if you have changed the port in the **.conf** use it instead of the 8080

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
MAX_IMAGE_SIZE - Max profile picture size
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
TEXT - Data in double quotation marks is returned as str.
SIZE - Data is returned as bytes supported scalars [B, K, M, G, T, P]
BOOLEAN - Data is returned as bool keywords are [TRUE, FALSE]
ARRAY - Data is TEXT seperated with comma
DICTIONARY - Data is seperated to TEXT key, value pairs seperated with comma
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

Creating indexes may take a while the program will show message "creating indexes!" this may take up to 10min.
Then start the program and see the difference!

## Data

In both cases db is filled with seed.py

### Non-Indexed
copy of my debug info
```
max: 21.798s
avg: 0.002s
/ 4 0.002s
/static/<path:filename> 123 0.001s
/picture/<int:pid> 71 0.0s
/stream/<vid> 126 0.001s
/view/<vid> 5 20.954s
/view/<vid>?offset 1 20.302s
/?SEARCH 2 0.348s
/users/ 1 0.007s
/account/<int:pid> 7 0.057s
/login 2 0.047s
/video?edit 1 0.435s
/video 1 0.008s
/video?upload 1 0.012s
/users/?SEARCH 1 0.003s
/settings/<query> 1 0.02s
```

### Indexed
copy of my debug info:
```
Debug info:
max: 0.595s
avg: 0.0s
/view/<vid> 6 0.006s
/static/<path:filename> 155 0.001s
/picture/<int:pid> 64 0.0s
/ 7 0.001s
/stream/<vid> 295 0.0s
/view/<vid>?offset 6 0.017s
/?SEARCH 8 0.326s
/users/ 1 0.007s
/login 4 0.059s
/video 1 0.003s
/video?upload 1 0.031s
/comment 2 0.015s
/account/<int:pid> 2 0.005s
/settings/<query> 1 0.001s
/login?out 1 0.0s
```

### Results

We can see significant speed up in the responce times.
Most significant speedup comes from comment queries.
