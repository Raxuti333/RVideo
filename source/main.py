from flask import Flask, redirect, request
from parse import config
from root import root_page, root_favicon
from profile import profile_page, profile_picture, profile_upload, profile_edit
from signup import signup_page, signup_create
from login import login_page, login_in, login_out
from video import video_page, video_upload, video_view, video_download, video_edit, video_update

app = Flask(__name__)

app.secret_key = config("SECRET_KEY")
app.config['MAX_CONTENT_LENGTH'] = int(config("MAX_CONTENT_LENGTH"))

@app.route("/", methods=["GET", "POST"])
def root():
    return root_page(app)

@app.route("/profile", methods=["GET", "POST"])
def profile():
    JTABLE = { "": profile_page, "pfp" : profile_picture, "upload": profile_upload, "edit": profile_edit, "delete": profile_page }

    try:
        key = str(request.query_string, "utf-8").split("=")[0]
        return JTABLE[key](app)
    except:
        return profile_page(app)
    
@app.route("/signup", methods=["GET", "POST"])
def signup():
    JTABLE = { "": signup_page, "create": signup_create }

    key = str(request.query_string, "utf-8")
    try:
        return JTABLE[key](app)
    except:
        return redirect("/sigup")
    
@app.route("/login", methods=["GET", "POST"])
def login():
    JTABLE = { "": login_page, "in": login_in, "out": login_out }

    key = str(request.query_string, "utf-8")
    try:
        return JTABLE[key](app)
    except:
        return redirect("/login")

@app.route("/video", methods=["GET", "POST"])
def video():
    JTABLE = { "": video_page, "upload": video_upload, "view": video_view, "download": video_download, "edit": video_edit, "update": video_update }

    try:
        key = str(request.query_string, "utf-8").split("=")[0]
        return JTABLE[key](app)
    except:
        return redirect("/")

@app.route("/favicon.ico")
def favicon():
    return root_favicon(app)

app.run("0.0.0.0", config("PORT"))