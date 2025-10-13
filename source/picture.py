""" send picture to client """

from flask import redirect
from util import config, get_filename, send_data

def picture(pid: int):
    """ fetch account picture """

    mimetype: dict[str, str] = config("IMAGE_MIMETYPES")

    path = get_filename(pid, "pfp", config("IMAGE_FILE_TYPES"))
    if path is None:
        return redirect("/static/no-pfp.png")

    return send_data(path, mimetype[path.split(".")[-1]])
