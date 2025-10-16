""" Handles http routing """

from flask import Flask
from util import config
import root
import account
import login
import comment
import video
import view
import stream
import picture
import debug

app: Flask = Flask(__name__, "/static", template_folder="html")

@app.route("/", methods=["GET"])
def route_root():
    """ route to landing page """
    return root.page()

@app.route("/account/<int:pid>", methods=["GET", "POST"])
def route_account(pid: int):
    """ routes account requests """
    return account.page(pid)

@app.route("/login", methods=["GET", "POST"])
def route_login():
    """ routes login requests """
    return login.page()

@app.route("/video", methods=["GET", "POST"])
def route_video():
    """ routes video requests """
    return video.page()

@app.route("/view/<vid>", methods=["GET"])
def route_view(vid: str):
    """ routes video page """
    return view.page(vid)

@app.route("/stream/<vid>", methods=["GET"])
def route_stream(vid: str):
    """ stream video """
    return stream.video(vid)

@app.route("/picture/<int:pid>", methods=["GET"])
def route_picture(pid: int):
    """ picture send """
    return picture.upload(pid)

@app.route("/comment", methods=["POST"])
def route_comment():
    """ routes comment requests """
    return comment.handle()

if config("DEBUG"):
    app.before_request(debug.before)
    app.after_request(debug.after)

app.secret_key = config("SECRET_KEY")
app.config["MAX_CONTENT_SIZE"] = config("MAX_FILE_SIZE")
app.run("0.0.0.0", config("PORT"), threaded=True)
