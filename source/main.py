from flask import Flask, send_file

app = Flask(__name__)

@app.route("/")
def root():
    return "Hello World"

@app.route("/favicon.ico")
def favicon():
    return send_file(app.root_path + "/favicon.ico", mimetype='image/vnd.microsoft.icon')

app.run("0.0.0.0", 8080)