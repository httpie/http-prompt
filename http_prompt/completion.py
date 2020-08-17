"""Meta data for autocomplete."""

try:
    from collections import OrderedDict
except ImportError:  # For Python 2.6, nocover
    from ordereddict import OrderedDict

from . import options as opt


ROOT_COMMANDS = OrderedDict([
    ('cd', 'Change URL/path'),
    ('clear', 'Clear console screen'),
    ('curl', 'Preview curl command'),
    ('env', 'Print environment'),
    ('exec', 'Clear and load environment from a file'),
    ('exit', 'Exit HTTP Prompt'),
    ('help', 'List commands, actions, and HTTPie options'),
    ('httpie', 'Preview HTTPie command'),
    ('rm *', 'Remove all options and parameters'),
    ('rm -b', 'Remove body parameter'),
    ('rm -b *', 'Remove all body parameters'),
    ('rm -h', 'Remove header'),
    ('rm -h *', 'Remove all headers'),
    ('rm -o', 'Remove HTTPie option'),
    ('rm -o *', 'Remove all HTTPie options'),
    ('rm -q', 'Remove querystring parameter'),
    ('rm -q *', 'Remove all querystring parameters'),
    ('source', 'Load environment from a file'),
])

ACTIONS = OrderedDict([
    ('connect', 'CONNECT request'),
    ('delete', 'DELETE request'),
    ('get', 'GET request'),
    ('head', 'HEAD request'),
    ('options', 'OPTIONS request'),
    ('patch', 'GET request'),
    ('post', 'POST request'),
    ('put', 'PUT request'),
])

# http://www.iana.org/assignments/message-headers/message-headers.xhtml
# https://en.wikipedia.org/wiki/List_of_HTTP_header_fields
HEADER_NAMES = OrderedDict([
    ('Accept', 'Acceptable response media type'),
    ('Accept-Charset', 'Acceptable response charsets'),
    ('Accept-Encoding', 'Acceptable response content codings'),
    ('Accept-Language', 'Preferred natural languages in response'),
    ('ALPN', 'Application-layer protocol negotiation to use'),
    ('Alt-Used', 'Alternative host in use'),
    ('Authorization', 'Authentication information'),
    ('Cache-Control', 'Directives for caches'),
    ('Connection', 'Connection options'),
    ('Content-Encoding', 'Content codings'),
    ('Content-Language', 'Natural languages for content'),
    ('Content-Length', 'Anticipated size for payload body'),
    ('Content-Location', 'Where content was obtained'),
    ('Content-MD5', 'Base64-encoded MD5 sum of content'),
    ('Content-Type', 'Content media type'),
    ('Cookie', 'Stored cookies'),
    ('Date', 'Datetime when message was originated'),
    ('Depth', 'Applied only to resource or its members'),
    ('DNT', 'Do not track user'),
    ('Expect', 'Expected behaviors supported by server'),
    ('Forwarded', 'Proxies involved'),
    ('From', 'Sender email address'),
    ('Host', 'Target URI'),
    ('HTTP2-Settings', 'HTTP/2 connection parameters'),
    ('If', 'Request condition on state tokens and ETags'),
    ('If-Match', 'Request condition on target resource'),
    ('If-Modified-Since', 'Request condition on modification date'),
    ('If-None-Match', 'Request condition on target resource'),
    ('If-Range', 'Request condition on Range'),
    ('If-Schedule-Tag-Match', 'Request condition on Schedule-Tag'),
    ('If-Unmodified-Since', 'Request condition on modification date'),
    ('Max-Forwards', 'Max number of times forwarded by proxies'),
    ('MIME-Version', 'Version of MIME protocol'),
    ('Origin', 'Origin(s) issuing the request'),
    ('Pragma', 'Implementation-specific directives'),
    ('Prefer', 'Preferred server behaviors'),
    ('Proxy-Authorization', 'Proxy authorization credentials'),
    ('Proxy-Connection', 'Proxy connection options'),
    ('Range', 'Request transfer of only part of data'),
    ('Referer', 'Previous web page'),
    ('TE', 'Transfer codings willing to accept'),
    ('Transfer-Encoding', 'Transfer codings applied to payload body'),
    ('Upgrade', 'Invite server to upgrade to another protocol'),
    ('User-Agent', 'User agent string'),
    ('Via', 'Intermediate proxies'),
    ('Warning', 'Possible incorrectness with payload body'),
    ('WWW-Authenticate', 'Authentication scheme'),
    ('X-Csrf-Token', 'Prevent cross-site request forgery'),
    ('X-CSRFToken', 'Prevent cross-site request forgery'),
    ('X-Forwarded-For', 'Originating client IP address'),
    ('X-Forwarded-Host', 'Original host requested by client'),
    ('X-Forwarded-Proto', 'Originating protocol'),
    ('X-Http-Method-Override', 'Request method override'),
    ('X-Requested-With', 'Used to identify Ajax requests'),
    ('X-XSRF-TOKEN', 'Prevent cross-site request forgery'),
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
