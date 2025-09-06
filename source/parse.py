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
    return wash(cut(open(".config").read(), field))

def validate(input: str) -> str:
    return input.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("[", "&#91;").replace("]", "&#93;").replace("$", "&#36;")