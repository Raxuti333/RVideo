# RVIDEO

## About
RVideo on simple video sharing website.

Features:
* Creating profiles ✅
* Adding profile picture ✅
* Uploading videos ✅
* Commenting on videos ❌
* Searching for profiles and videos ❌

## Structure

### Source
All static data such as **code**, **html** and **logo**'s are stored in the source directory.

html files are seperated in to source/html.
static images are in source/images

### Environment
The **env** folder contains an example environment for the program.

The point of the **env** is to contain the running enviroment of the program. Such as DB and video and dynamic images.

The **env** contains the **.config** files where the program configurations are stored more about the **.config** in the [Runnig:Config](#config) section.

#### Scripts
In the **env** folder there are script **run.sh** the script can be used to run the program. If you move the **env** folder remember to update the paths in the script.

The script creates the **db** if one is not found in the environment folder.

## Running

### Python

This project has been developed on CPython 3.13.1

### Downloading
Clone the master branch to your local computer and move to directory
```sh
git clone git@github.com:Raxuti333/RVideo.git && cd RVideo
```

### Virtual environment
Now create a virtual python environment and activate it
```sh
python -m venv .venv && source .venv/bin/activate
```

### Dependencies
This program uses **flask** and **sqlite**. 
While **sqlite** is bundled with CPython i don't know if this is in the python spec so if you are running this with no CPython beawere.

Then install flask
```sh
pip install flask
```

### Config
The .config file uses simple quite simple syntax.
```
[FIELD data]
```
Currently used fields are:
```
PORT port which the program listens
SECRET_KEY secret key of the program
MAX_CONTENT_LENGTH maximum accepted file size
```

Now you need to edit the **env/.config** file and replace the secret key and set the port.

Example **.config** file:
```
[PORT 8080]

[SECRET_KEY 1d7a6df767ab3fa7aa0377937632322f]

[MAX_CONTENT_LENGTH 2000000000]
```
The secret key is a random string with arbitary lenght.
Note that the secret key should not be too short.

### Run
Now you can just start the program with:
```
env/run.sh
```

## Security

CSRF prevented with session token embeding on forms.