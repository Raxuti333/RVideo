""" TODO """

from flask import Flask
from util import config
import root, account, video

app: Flask = Flask(__name__, "/static", template_folder="html")

@app.route("/", methods=["GET", "POST"])
def route_root():
    """ route to landing page """
    return root.root_page()

@app.route("/account", methods=["GET", "POST"])
def route_account():
    """ TODO """
    return ""

@app.route("/video", methods=["GET", "POST"])
def route_video():
    """ TODO """
    return ""

@app.route("/comment", methods=["POST"])
def route_comment():
    """ TODO """
    return ""

app.secret_key = config("SECRET_KEY")
app.run("0.0.0.0", config("PORT"))
