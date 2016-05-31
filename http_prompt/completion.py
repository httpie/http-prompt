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

HEADER_NAMES = OrderedDict([
    ('Accept', 'Header'),
    ('Accept-Charset', 'Header'),
    ('Accept-Encoding', 'Header'),
    ('Accept-Language', 'Header'),
    ('Accept-Datetime', 'Header'),
    ('Authorization', 'Header'),
    ('Cache-Control', 'Header'),
    ('Connection', 'Header'),
    ('Cookie', 'Header'),
    ('Content-Length', 'Header'),
    ('Content-MD5', 'Header'),
    ('Content-Type', 'Header'),
    ('Date', 'Header'),
    ('Expect', 'Header'),
    ('Forwarded', 'Header'),
    ('From', 'Header'),
    ('Host', 'Header'),
    ('If-Match', 'Header'),
    ('If-Modified-Since', 'Header'),
    ('If-None-Match', 'Header'),
    ('If-Range', 'Header'),
    ('If-Unmodified-Since', 'Header'),
    ('Max-Forwards', 'Header'),
    ('Origin', 'Header'),
    ('Pragma', 'Header'),
    ('Proxy-Authorization', 'Header'),
    ('Range', 'Header'),
    ('Referer', 'Header'),
    ('TE', 'Header'),
    ('User-Agent', 'Header'),
    ('Upgrade', 'Header'),
    ('Via', 'Header'),
    ('Warning', 'Header'),
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
