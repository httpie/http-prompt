from __future__ import unicode_literals

import math
import re

from prompt_toolkit.shortcuts import create_output
from six.moves import range
from six.moves.urllib.parse import urlparse


RE_ANSI_ESCAPE = re.compile(r'\x1b[^m]*m')


def smart_quote(s):
    # TODO: Escape
    if ' ' in s or r'\:' in s:
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


def unescape(s, exclude=None):
    if exclude:
        char = '[^%s]' % exclude
    else:
        char = '.'
    return re.sub(r'\\(%s)' % char, r'\1', s)


def get_terminal_size():
    return create_output().get_size()


def strip_ansi_escapes(text):
    return RE_ANSI_ESCAPE.sub('', text)


def colformat(strings, num_sep_spaces=1, terminal_width=None):
    """Format a list of strings like ls does multi-column output."""
    if terminal_width is None:
        terminal_width = get_terminal_size().columns

    if not strings:
        return

    num_items = len(strings)
    max_len = max([len(strip_ansi_escapes(s)) for s in strings])

    num_columns = min(
        int((terminal_width + num_sep_spaces) / (max_len + num_sep_spaces)),
        num_items)
    num_columns = max(1, num_columns)

    num_lines = int(math.ceil(float(num_items) / num_columns))
    num_columns = int(math.ceil(float(num_items) / num_lines))

    num_elements_last_column = num_items % num_lines
    if num_elements_last_column == 0:
        num_elements_last_column = num_lines

    lines = []
    for i in range(num_lines):
        line_size = num_columns
        if i >= num_elements_last_column:
            line_size -= 1
        lines.append([None] * line_size)

    for i, line in enumerate(lines):
        line_size = len(line)
        for j in range(line_size):
            k = i + num_lines * j
            item = strings[k]
            if j % line_size != line_size - 1:
                item_len = len(strip_ansi_escapes(item))
                item = item + ' ' * (max_len - item_len)
            line[j] = item

    sep = ' ' * num_sep_spaces
    for line in lines:
        yield sep.join(line)

def get_prompt(url, fmt):
    """Generate a prompt following the user config prompt format."""
    prompt = []
    whitelist = [ 'scheme', 'netloc', 'path', 'params', 'query', 'fragment' ]
    parse_result = urlparse(url)

    for w in filter(bool, fmt.replace('{', '').split('}')):
        try:
            attribute = re.search('^[a-z_]+', w).group(0)
        except AttributeError:
            return url
        if attribute not in whitelist:
            return url
        try:
            index = re.search('\[([-?0-9:?])+\]', w).group(0)
            if attribute == 'path':
                path_slice = eval('parse_result.path.split(\'/\')' + index)
                join = '/'.join(path_slice)
                new_path = join[1:] if join.startswith('/') else join
                prompt.append('/' + new_path)
            elif attribute == 'netloc':
                netloc_slice = eval('parse_result.netloc.split(\'.\')' + index)
                new_netloc = '.'.join(netloc_slice)
                prompt.append(new_netloc)
            else:
                raise AttributeError
        except AttributeError:
            if attribute == 'scheme':
                prompt.append(parse_result.scheme + '://')
            elif attribute == 'query' and parse_result.query:
                prompt.append('?' + parse_result.query)
            elif attribute == 'fragment' and parse_result.fragment:
                prompt.append('#' + parse_result.fragment)
            else:
                prompt.append(getattr(parse_result, attribute))
    return ''.join(prompt)
