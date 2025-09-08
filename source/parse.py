import db, re

VIDEO_HTML: str = """ 
<a href=\"video?view=$VID\" style=\"text-decoration: none; display: inline;\">
    <img style=\"display: inline; width: 48px; heigth: 48px\" src=\"profile?pfp=$PID\">
    <p style=\"display: inline; position: relative; bottom: 15px;\">$TITLE</p>
</a>
"""

def cut(html: str, block: str) -> str:
    key: str = "[" + block
    i: int = html.find(key)
    if i == -1: return html
    return html[:i] + html[i + len(key):].replace("]", "", count=1)

# wash off unselected
def wash(html: str) -> str:
    b: int = html.find("[")
    while b != -1:
        e: int = html[b:].find("]") + 1
        if e == 0: break
        html = html[:b] + html[(b + e):]
        b = html.find("[")
    return html

def config(field: str) -> str:
    # Replace with non-garbage collection reliant method
    return wash(cut(open(".config").read(), field)).replace("\n", "").replace(" ", "")

def validate(input: str) -> str:
    return input.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("[", "&#91;").replace("]", "&#93;").replace("$", "&#36;")

def search(req: str):
    html: str = ""

    limit = 20
    params = []
    sql: str = "SELECT * FROM video"

    # Generate sql query with parameters 
    for m in req.split(","):
        p = m.split("=")
        match(p[0]):
            case "BEFORE":
                if re.match(r"^\d{2}-\d{2}-\d{4}$", p[-1]) or p[-1] == "now":
                    sql += f" WHERE timediff(date, '{p[-1]}') > 0"
            case "AFTER":
                if re.match(r"^\d{2}-\d{2}-\d{4}$", p[-1]) or p[-1] == "now":
                    sql += f" WHERE timediff(date, '{p[-1]}') < 0"
            case "USER":
                user = db.query("SELECT pid FROM profile WHERE LOWER(username) = LOWER(?)", [p[-1]])
                if user != []:
                    sql += f" WHERE pid = {user[0]["pid"]}"
                else:
                    sql += " WHERE pid = 0"
            case "USERS":
                users = db.query("SELECT pid FROM profile WHERE username LIKE ?", ["%" + p[-1] + "%"], 5)
                if users != []:
                    sql += " WHERE"
                    for u in users:
                        sql += f" pid = {u["pid"]} OR"
                    sql = sql[:len(sql) - 2]
            case "LIMIT":
                if p[-1].isdigit(): 
                    if int(p[-1]) < 100:
                        limit = int(p[-1])
            case _:
                sql += " WHERE"
                for x in m.split(" "):
                    params.append("%"+x+"%")
                    sql += " name LIKE ? OR"
                sql = sql[:len(sql) - 2]

    videos = db.query(sql, params, limit)
    for v in videos:
        html += VIDEO_HTML.replace("$VID", str(v["vid"])).replace("$PID", str(v["pid"])).replace("$TITLE", v["name"])

    return html