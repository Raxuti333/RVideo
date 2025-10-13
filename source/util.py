""" all utility functions and frequently used functions """

import re
import builtins
from string import ascii_uppercase, ascii_lowercase
from os import SEEK_SET, SEEK_END
from os.path import isfile
from secrets import token_hex
from io import BytesIO
from flask import session, request, flash, get_flashed_messages, send_file
from werkzeug.datastructures import FileStorage

EXPRESSION = re.compile(r"^(\d+|\d+_\d+)$")
PRIVATEVID = re.compile(r"^\d+_\d+$")

SIZES: dict[str, int] = {
    "B": 1,
    "K": 1024,
    "M": 1048576,
    "G": 1073741824,
    "T": 1099511627776,
    "P": 1125899906842624
}

# all registered mp4 types with mimetype of video/mp4
# https://www.ftyps.com/#2
VIDEO_TYPES: list[bytes] = [
    bytes("avc1", "utf-8"),
    bytes("iso2", "utf-8"),
    bytes("isom", "utf-8"),
    bytes("mmp4", "utf-8"),
    bytes("mp41", "utf-8"),
    bytes("mp42", "utf-8"),
]

configs: dict[str, str | int | bool] = {}

def get_flash() -> list[str]:
    """ get messages from flash """
    flashed: list[str] = get_flashed_messages()
    if flashed == []:
        return [""]
    return flashed

def set_flash(messages: list[str]) -> None:
    """ set messages to flash """
    for msg in messages:
        flash(msg)

def get_token() -> str:
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

def clear_account() -> None:
    """ clears account from session """
    session.pop("account")

def get_form(fields: list[tuple[str, type | str]]) -> dict[str, builtins.any]:
    """ returns dictionary containing fields values """
    form: dict[str, builtins.any] = {}
    for f, t in fields:
        match(t):
            case "FILE":
                form[f] = request.files.get(f)
            case builtins.bool:
                form[f] = request.form.get(f, type=str) == "True"
            case _:
                form[f] = request.form.get(f, type=t)
    return form

def get_query(seperator: str) -> list[str]:
    """ returns query strings list """
    binary: bytes = request.query_string
    if not binary:
        return [""]
    return str(binary, encoding="utf-8").split(seperator)

def get_method() -> str:
    """ returns request method """
    return request.method

def get_range() -> int:
    """ gets range from header """
    hrange: str = request.headers.get("range")
    if hrange is None:
        return 0

    hrange = hrange[6:hrange.find("-")]

    if hrange.isdigit():
        return int(hrange)

    return 0

def get_tags(text: str) -> list[str]:
    """ returns a string only containing tags found in text """
    tags: list[str] = []
    index: int = text.find("#")
    while index != -1:
        space = text.find(" ", index)
        next_htag = text.find("#", index + 1)

        key: int = 2 * (space == -1) + (next_htag == -1)

        match(key):
            case 0:
                end = space if space < next_htag else next_htag
            case 1:
                end = space
            case 2:
                end = next_htag
            case 3:
                end = len(text)

        tags.append(text[index:end].replace("\n", ""))
        index = next_htag
    return tags

def get_filename(fid: int | str, root: str, types: list[str]) -> str | None:
    """ returns files relative path """

    match(type(fid)):
        case builtins.int:
            fid = str(fid)
        case _:
            pass

    if EXPRESSION.match(fid) is None:
        return None

    for t in types:
        path: str = root + "/" + fid + "." + t
        if isfile(path):
            return path
    return None

def get_vid(vid: str | None) -> tuple[int, int] | tuple[None, None]:
    """ extract vid from vid string """
    if vid is None:
        return (None, None)
    if PRIVATEVID.match(vid) is not None:
        parts: list[str] = vid.split("_")
        return (int(parts[1]), int(parts[0]))
    if vid.isdigit():
        return (int(vid), None)
    return (None, None)

def check_file(file: FileStorage, max_size: int, types: list[str]) -> tuple[bool, str]:
    """ checks if file is acceptable """

    if file.filename == "":
        return (False, "No file selected")

    file_type: str = file.filename.split(".")[-1]
    if file_type not in types:
        return (False,
        f"File type { file_type } is not supported!\n"
        f"Use: { str(types).replace("[", "").replace("]", "").replace("'", "") }"
        )

    file.seek(0, SEEK_END)
    if file.tell() > max_size:
        return (False,
        f"File is { int_to_size(file.tell()) } while maximum is { int_to_size(max_size) }"
        )
    file.seek(0, SEEK_SET)

    return (True, "Success")

def check_video(file: FileStorage, max_size: int) -> tuple[bool, str]:
    """ checks if video is acceptable """

    if file.filename == "":
        return (False, "No file selected")

    file_type: str = file.filename.split(".")[-1].lower()
    if file_type != "mp4":
        return (False, f"file type { file_type } is not supported")

    file.seek(4, SEEK_SET)
    ftyp: bytes = file.read(8)

    if ftyp[:4] != bytes("ftyp", "utf-8"):
        return (False, "file header is non-standard mp4")

    if ftyp[4:] not in VIDEO_TYPES:
        return (False,
        f"mp4's with ftyp: { str(ftyp[4:], 'utf-8') } are not supported"
        )

    file.seek(0, SEEK_END)
    if file.tell() > max_size:
        return (False,
        f"File is { int_to_size(file.tell()) } while maximum is { int_to_size(max_size) }"
        )
    file.seek(0, SEEK_SET)

    return (True, "Success")

def send_data(path: str, mimetype: str):
    """ sends file with mimetype """
    with open(path, "rb") as fd:
        return send_file(BytesIO(fd.read()), mimetype=mimetype)

def check_password(password: str) -> tuple[bool, str]:
    """ checks if password is acceptable """
    if len(password) < 4:
        return (False, "Password must be longer than 3 character")
    if not any(ch in password for ch in ascii_lowercase):
        return (False, "passoword must contain at least 1 lowercase letter")
    if not any(ch in password for ch in ascii_uppercase):
        return (False, "passoword must contain at least 1 uppercase letter")
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

    value = configs.get(field)
    if value is not None:
        return value

    with open(".config", encoding="utf-8") as fd:
        file: str = fd.read()

    begin: int = file.find("[" + field)
    end: int = file.find("]", begin)

    type_begin: int = file.find(":", begin)
    type_end: int = file.find(" ", type_begin)

    type_info: str = file[type_begin + 1:type_end]

    data: str = file[type_end + 1:end]

    match(type_info):
        case "INTEGER":
            value = int(data)
        case "SIZE":
            value = int(data.replace(data[-1], "")) * SIZES[data[-1]]
        case "BOOLEAN":
            value = data == "TRUE"
        case "ARRAY":
            value = data.replace(" ", "").split(",")
        case "DICTIONARY":
            value = {}
            for element in data[1:-1].split(","):
                parts: list[str] = element.replace(" ", "").split(":")
                value[parts[0]] = parts[1]
        # TEXT is default case
        case _:
            value = data

    configs[field] = value
    return value

def int_to_size(number: int) -> str:
    """ converts integer to human readable size """
    for size in SIZES.items().__reversed__():
        if number >= size[1]:
            value: str = str(float(number) / float(size[1]))
            return value[:value.find(".") + 2] + size[0]

    return "NaS"
