"""Meta data for autocomplete."""


try:
    from collections import OrderedDict
except ImportError:  # For Python 2.6, nocover
    from .ordereddict import OrderedDict

from . import options as opt


ROOT_COMMANDS = OrderedDict([
    ('cd', 'Change URL/path'),
    ('curl', 'Preview curl command'),
    ('exit', 'Exit HTTP Prompt'),
    ('help', 'List commands, actions, and HTTPie options'),
    ('httpie', 'Preview HTTPie command'),
    ('rm *', 'Remove all options and parameters'),
    ('rm -b', 'Remove body parameter'),
    ('rm -h', 'Remove header'),
    ('rm -o', 'Remove HTTPie option'),
    ('rm -q', 'Remove querystring parameter'),
])

ACTIONS = OrderedDict([
    ('delete', 'DELETE request'),
    ('get', 'GET request'),
    ('head', 'HEAD request'),
    ('patch', 'GET request'),
    ('post', 'POST request'),
    ('put', 'PUT request'),
])

# TODO: Include more header names
HEADER_NAMES = OrderedDict([
    ('Accept', 'Header'),
    ('Accept-Encoding', 'Header'),
    ('Authorization', 'Header'),
    ('Cache-Control', 'Header'),
    ('Cookie', 'Header'),
    ('Content-Length', 'Header'),
    ('Content-Type', 'Header'),
    ('From', 'Header'),
    ('Host', 'Header'),
    ('Origin', 'Header'),
    ('Referer', 'Header'),
    ('User-Agent', 'Header'),
])

CONTENT_TYPES = [
    'application/json',
    'application/x-www-form-urlencoded',
    'multipart/form-data',
    'text/html',
]

# TODO: Include more common header values
HEADER_VALUES = {
    'Accept': CONTENT_TYPES,
    'Content-Type': CONTENT_TYPES,
}

OPTION_NAMES = sorted(opt.FLAG_OPTIONS + opt.VALUE_OPTIONS)
OPTION_NAMES = OrderedDict(OPTION_NAMES)
