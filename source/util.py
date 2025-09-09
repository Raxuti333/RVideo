""" TODO """

from secrets import token_hex
from flask import session

def get_session_token() -> str:
    """ return existing session token or create a session token """
    if session.get("token") is None:
        session["token"] = token_hex(16)
    return session["token"]

def config(field: str) -> str:
    """ returns fields value from .config """
    with open(".config", encoding="utf-8") as fd:
        file: str = fd.read()

    begin: int = file.find("[" + field)
    end: int = file.find("]", begin)

    return file[:end][begin + len(field) + 2:]
