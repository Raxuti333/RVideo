import re, db

VIDEO_HTML: str = """
<a href=\"video?view=$VID\" class="video">
    <img style=\"display: inline; width: 48px; heigth: 48px\" src=\"profile?pfp=$PID\">
    <p style=\"display: inline; position: relative; bottom: 15px;\">$TITLE</p>
</a>
"""

def replace(html: str, params: list[tuple]) -> str:
    """ replaces all listed parameters """
    for p in params:
        html = html.replace(p[0], p[1])
    return html

def read(local_path: str) -> str:
    """ read utf-8 encoded text file """
    with open(local_path, encoding="utf-8") as f:
        return f.read()

def cut(html: str, block: str) -> str:
    """ cut field """
    key: str = "[" + block
    i: int = html.find(key)
    if i == -1: return html
    return html[:i] + html[i + len(key):].replace("]", "", count=1)

def wash(html: str) -> str:
    """ remove uncut fields """
    b: int = html.find("[")
    while b != -1:
        e: int = html[b:].find("]") + 1
        if e == 0: break
        html = html[:b] + html[(b + e):]
        b = html.find("[")
    return html

def config(field: str) -> str:
    """ read field from .config """
    return wash(cut(read(".config"), field)).replace("\n", "").replace(" ", "")

def validate(user_str: str) -> str:
    """ validate user input """
    return user_str.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("[", "&#91;").replace("]", "&#93;").replace("$", "&#36;")

def search(req: str):
    """ search for video in db """
    html: str = ""

    limit = 20
    params = []
    sql: str = "SELECT * FROM video WHERE"

    # Generate sql query with parameters
    for m in req.split(","):
        p = m.split("=")
        match(p[0]):
            case "BEFORE":
                if re.match(r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$", p[-1]) is not None or p[-1] == "now":
                    sql += f" (strftime(\"%s\", date) - strftime(\"%s\", \"{p[-1]}\")) < 0"
                else: sql += " 1"
                sql += " AND"
            case "AFTER":
                if re.match(r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$", p[-1]) is not None or p[-1] == "now":
                    sql += f" (strftime(\"%s\", date) - strftime(\"%s\", \"{p[-1]}\")) > 0"
                else: sql += " 1"
                sql += " AND"
            case "USER":
                user = db.query("SELECT pid FROM profile WHERE LOWER(username) = LOWER(?)", [p[-1]])
                if user != []:
                    sql += f" pid = {user[0]["pid"]} AND"
                else: sql += " pid = 0 AND"
            case "USERS":
                users = db.query("SELECT pid FROM profile WHERE LOWER(username) LIKE LOWER(?)", [p[-1] + "%"], 10)
                if users != []:
                    for u in users:
                        sql += f" pid = {u["pid"]} OR"
                    sql = sql[:len(sql) - 2] + " AND"
                else: sql += " pid = 0 AND"
            case "LIMIT":
                if p[-1].isdigit(): 
                    if int(p[-1]) < 100:
                        limit = int(p[-1])
            case _:
                for x in m.split(" "):
                    params.append("%"+x+"%")
                    sql += " name LIKE ? OR"
                sql = sql[:len(sql) - 2] + "AND"

    sql = sql[:len(sql) - 4]

    videos = db.query(sql, params, limit)
    for v in videos:
        html += replace(
            VIDEO_HTML,
            [("$VID", str(v["vid"])),
             ("$PID", str(v["pid"])),
             ("$TITLE", v["name"])]
            )

    return html
