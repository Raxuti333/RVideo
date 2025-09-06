from flask import Flask, session, send_file
from parse import cut, wash

def page(app: Flask):
    # Replace with non-garbage collection reliant method
    html: str = open(app.root_path + "/html/profile.html").read()

    if session.get("profile") == None:
        return wash(cut(html, "NO_PROFILE"))
    
    html = cut(html, "PROFILE")

    html = wash(html)
    return html

# Support profile pictures
def pfp(app: Flask):
    if session.get("profile") == None:
        return send_file(app.root_path + "/no-pfp.png", mimetype='image/png')
    return send_file(app.root_path + "/no-pfp.png", mimetype='image/png')