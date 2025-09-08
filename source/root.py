""" TODO """

from flask import render_template

def root_page() -> str:
    """ service function for landing page """
    return render_template("root.html")
