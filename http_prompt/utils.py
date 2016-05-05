from __future__ import unicode_literals

import re


def smart_quote(s):
    # TODO: Escape
    if ' ' in s:
        s = "'" + s + "'"
    return s


def unescape(s):
    return re.sub(r'\\(.)', r'\1', s)
