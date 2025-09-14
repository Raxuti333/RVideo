""" Landing page processing i.e video search functions """

from flask import render_template
from util import get_session_token, get_account, get_form

def root_page() -> str:
    """ service function for landing page """

    token   = get_session_token()
    account = get_account()
    form    = get_form([
                         ("search", str),
                         ("select", str),
                         ("date",   str),
                         ("user",   str),
                         ("token",  str)
                        ])
    
    return render_template("root.html", token=token, account=account)
