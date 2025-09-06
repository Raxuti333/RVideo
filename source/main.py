from flask import Flask, send_file, session, request
from parse import cut, wash, config
from profile import pfp, page

app = Flask(__name__)

app.secret_key = config("SECRET_KEY")

@app.route("/")
def root():
    # Replace with non-garbage collection reliant method
    html: str = open(app.root_path + "/html/root.html").read()

    # Add support embeding username
    if session.get("profile") != None:
        html = cut(html, "Profile")
    else:
        html = cut(html, "Login")

    html = wash(html)

    return html

@app.route("/profile")
def profile():
    JTABLE = { "": page, "pfp" : pfp, }

    key = str(request.query_string, "utf-8")
    try:
        return JTABLE[key](app)
    except:
        return "Failed to query " + key, 400


@app.route("/favicon.ico")
def favicon():
    return send_file(app.root_path + "/favicon.ico", mimetype='image/vnd.microsoft.icon')

app.run("0.0.0.0", config("PORT"))