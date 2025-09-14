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
    return session.get("account")

def set_account(account: dict) -> None:
    """ sets value to account if it's found """
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

def get_method() -> str:
    """ returns request method """
    return request.method

def check_password(password: str) -> tuple[bool, str]:
    """ checks if password is acceptable """
    if len(password) < 4:
        return (False, "password too short")
    if not any(ch in password for ch in r"1234567890 _\?!@$%{}[]\+-/\\"):
        return (False, "password must contain at leas one special character")
    return (True, "Success")

def check_username(username: str) -> tuple[bool, str]:
    """ checks if username is acceptable """
    if len(username) == 0:
        return (False, "username too short")
    return (True, "Success")

def config(field: str) -> str | int:
    """ returns fields value from .config """
    with open(".config", encoding="utf-8") as fd:
        file: str = fd.read()

    begin: int = file.find("[" + field)
    end: int = file.find("]", begin)

    type_begin: int = file.find(":", begin)
    type_end: int = file.find(" ", type_begin)

    type_info: str = file[:type_end][type_begin + 1:]

    data: str = file[:end][type_end + 1:]

    match(type_info):
        case "INTEGER":
            return int(data)
        case "SIZE":
            multiplier: dict[str, int] = {
                "B": 1,
                "K": 1024,
                "M": 1048576,
                "G": 1073741824,
                "T": 1099511627776,
                "P": 1125899906842624
            }
            return int(data.replace(data[-1], "")) * multiplier[data[-1]]
        # TEXT is default case
        case _:
            return data
