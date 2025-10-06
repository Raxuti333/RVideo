""" debug timing info """

from time import time
from flask import request
from util import config

class Debug:
    """ hold debug info """
    def __init__(self):
        self.avg = 0
        self.max = 0
        self.urls: dict[str, tuple[float, int]] = {}

    def __del__(self):
        print("\n\033[32mDebug info\033[0m:")

        dump: str = f"max: { str(round(self.max, 3)) }s\navg: { str(round(self.avg, 3)) }s\n"

        for url, metric in self.urls.items():
            dump += url + f" {metric[1]} { str(round(metric[0], 3)) }s\n"
        print(dump)

    def push(self, url, delta_time):
        """ push new data point """
        if self.avg == 0:
            self.avg = delta_time
        if self.urls.get(url) is None:
            self.urls[url] = (delta_time, 1)
        else:
            metric = self.urls[url]
            metric = ((metric[0] + delta_time) / 2, metric[1] + 1)
            self.urls[url] = metric
        self.max = max(self.max, delta_time)
        self.avg = (self.avg + delta_time) / 2

class Tracker:
    """ track container """
    def __init__(self, container):
        self.url = str(container.url_rule)
        query = str(container.query_string, "utf-8").split("=", maxsplit=1)[0]
        if query != "":
            self.url += "?" + query
        self.time = time()

    def __del__(self):
        delta_time = time() - self.time
        debug.push(self.url, delta_time)

    def __repr__(self):
        return self.url + " " + str(round(time() - self.time, 3)) + "s"

def before():
    """ attach tracker """
    request.track = Tracker(request)

def after(res):
    """ remove tracker """
    if config("PRINTS"):
        print(str(request.track))
    del request.track
    return res

debug = Debug()
