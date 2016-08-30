from __future__ import unicode_literals
import re


def smart_quote(s):
    # TODO: Escape
    if ' ' in s:
        s = "'" + s + "'"
    return s


def unquote(s):
    quotes = ["'", '"']
    quote_str = None
    if s[0] in quotes:
        quote_str = s[0]

    if quote_str and s[-1] == quote_str:
        return s[1: -1]
    return s


def unescape(s):
    return re.sub(r'\\(.)', r'\1', s)


def strip_color_codes(s):
    # Strips ANSI color codes from string
    return re.sub(
        u"[\u001b\u009b][[()#;?]*(?:[0-9]{1,4}(?:;[0-9]{0,4})*)?[0-9A-ORZcf-nqry=><]",
        "",
     s)
