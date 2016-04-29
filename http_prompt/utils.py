from __future__ import unicode_literals


def smart_quote(s):
    # TODO: Escape
    if ' ' in s:
        s = "'" + s + "'"
    return s
