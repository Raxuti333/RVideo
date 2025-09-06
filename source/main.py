from flask import Flask, send_file, session, request
from parse import cut, wash, config
from profile import profile_page, profile_picture
from signup import signup_page, signup_create
from login import login_page, login_in
import db

app = Flask(__name__)

app.secret_key = config("SECRET_KEY")

@app.route("/")
def root():
    # Replace with non-garbage collection reliant method
    html: str = open(app.root_path + "/html/root.html").read()

    # Add support embeding username
    if session.get("profile") != None:
        html = cut(html.replace("$USERNAME", session["profile"]["username"]), "Profile")
    else:
        html = cut(html, "Login")

    html = wash(html)

    return html

@app.route("/profile")
def profile():
    JTABLE = { "": profile_page, "pfp" : profile_picture, }

    key = str(request.query_string, "utf-8")
    try:
        return JTABLE[key](app)
    except:
        return "<p>Failed to query " + key + "</p>", 400
    
@app.route("/signup", methods=["GET", "POST"])
def signup():
    JTABLE = { "": signup_page, "create": signup_create }

    key = str(request.query_string, "utf-8")
    try:
        return JTABLE[key](app)
    except:
        return "<p>Failed to query " + key + "</p>", 400
    
@app.route("/login", methods=["GET", "POST"])
def login():
    JTABLE = { "": login_page, "in": login_in }

    key = str(request.query_string, "utf-8")
    try:
        return JTABLE[key](app)
    except:
        return "<p>Failed to query " + key + "</p>", 400

@app.route("/favicon.ico")
def favicon():
    return send_file(app.root_path + "/images/favicon.ico", mimetype='image/vnd.microsoft.icon')

app.run("0.0.0.0", config("PORT"))