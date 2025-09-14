""" TODO """

from secrets import token_hex
from flask import session, request, flash, get_flashed_messages

def get_flash() -> list[str]:
    """ get messages from flash """
    flashed = get_flashed_messages()
    if flashed == []:
        return [""]
    return flashed

def set_flash(messages: list[str]) -> None:
    """ set messages to flash """
    for msg in messages:
        flash(msg)

def get_session_token() -> str:
    """ return existing session token or create a session token """
    if session.get("token") is None:
        session["token"] = token_hex(16)
    return session["token"]

def get_account() -> dict | None:
    """ returns account or none if it isn't found """
    if session.get("account") is None:
        return None
    return session["account"]

def set_account(account: dict) -> None:
    """ sets value to account if it's found """
    if session.get("account") is None:
        return
    session["account"] = account

def get_form(fields: list[(str, type)]) -> dict:
    """ returns dictionary containing fields values """
    form: dict = {}
    for f, t in fields:
        if t is bool:
            form[f] = request.form.get(f, type=str) == "True"
        else:
            form[f] = request.form.get(f, type=t)
    return form

def get_query() -> list[str]:
    """ 
        returns query strings list 
        TODO support complex queries
    """
    binary: bytes = request.query_string
    if not binary:
        return [""]
    return str(binary, encoding="utf-8").split("=")

def check_password(password: str) -> tuple[bool, str]:
    """ checks if password is acceptable """
    if len(password) < 4:
        return (False, "password too short")
    if not any(ch in password for ch in r"1234567890 _\?!@$%{}[]\+-/\\"):
        return (False, "password must contain at leas one special character")
    return (True, "Success")

def config(field: str) -> str:
    """ returns fields value from .config """
    with open(".config", encoding="utf-8") as fd:
        file: str = fd.read()

    begin: int = file.find("[" + field)
    end: int = file.find("]", begin)

    return file[:end][begin + len(field) + 2:]
