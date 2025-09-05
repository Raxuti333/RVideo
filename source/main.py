from flask import Flask, send_file, session
from parse import cut, wash, config

app = Flask(__name__)

app.secret_key = config("SECRET_KEY")

@app.route("/")
def root():
    html: str = open(app.root_path + "/html/root.html").read()

    if session.get("profile") != None:
        html = cut(html, "Profile")
    else:
        html = cut(html, "Login")

    html = wash(html)

    return html

@app.route("/favicon.ico")
def favicon():
    return send_file(app.root_path + "/favicon.ico", mimetype='image/vnd.microsoft.icon')

app.run("0.0.0.0", config("PORT"))