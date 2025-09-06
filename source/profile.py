from flask import Flask, session, send_file, redirect
from parse import cut, wash

def profile_page(app: Flask):
    # Replace with non-garbage collection reliant method
    html: str = open(app.root_path + "/html/profile.html").read()

    if session.get("profile") == None:
        return redirect("/")

    html = wash(html)
    return html

# Support profile pictures
def profile_picture(app: Flask):
    if session.get("profile") == None:
        return send_file(app.root_path + "/images/no-pfp.png", mimetype='image/png')
    return send_file(app.root_path + "/images/no-pfp.png", mimetype='image/png')