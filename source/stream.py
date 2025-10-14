""" stream video data """

from os import SEEK_SET, SEEK_END
from flask import abort, redirect, Response
from util import config, get_account, get_filename, get_range, get_vid

def video(query: str):
    """ stream requested video """

    account = get_account()

    vid, pid = get_vid(query)
    if pid is not None and account is not None:
        if pid != account["pid"]:
            return abort(403)

    if vid is None:
        return redirect("/")

    path: str = get_filename(query, "video", ["mp4"])
    if path is None:
        return abort(404)

    start: int = get_range()

    with open(path, "rb") as file:
        chunk_size: int = config("CHUNK_SIZE")

        file.seek(0, SEEK_END)
        size: int = file.tell()

        end: int = min(start + chunk_size, size - 1)

        file.seek(start, SEEK_SET)
        chunk: bytes = file.read(chunk_size)

    headers = {
    "Content-Range": f"bytes {start}-{end}/{size}",
    "Accept-Ranges": "bytes",
    "Content-Length": end - start + 1,
    "Content-Type": "video/mp4",
    }

    return Response(chunk, 206, headers)
