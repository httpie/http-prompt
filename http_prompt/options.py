"""Meta data for HTTPie options."""

FLAG_OPTIONS = [
    ('--body', 'Print only response body'),
    ('--check-status', 'Check HTTP status code'),
    ('--continue', 'Resume an interrupted download'),
    ('--debug', 'Print debug information'),
    ('--download', 'Download as a file'),
    ('--follow', 'Allow full redirects'),
    ('--form', 'Send as form fields'),
    ('--headers', 'Print only response headers'),
    ('--help', 'Show tool (HTTPie, cURL) help message'),
    ('--ignore-stdin', 'Do not read stdin'),
    ('--json', 'Send as a JSON object (default)'),
    ('--stream', 'Stream the output'),
    ('--traceback', 'Print exception traceback'),
    ('--verbose', 'Print the whole request and response'),
    ('--version', 'Show version'),
    ('-b', 'Shorthand for --body'),
    ('-c', 'Shorthand for --continue'),
    ('-d', 'Shorthand for --download'),
    ('-f', 'Shorthand for --form'),
    ('-h', 'Shorthand for --headers'),
    ('-j', 'Shorthand for --json'),
    ('-S', 'Shorthand for --stream'),
    ('-v', 'Shorthand for --verbose'),
]

VALUE_OPTIONS = [
    ('--auth', 'Do authentication'),
    ('--auth-type', 'Authentication mechanism to be used'),
    ('--cert', 'Specify client SSL certificate'),
    ('--cert-key', 'The private key to use with SSL'),
    ('--output', 'Save output to a file'),
    ('--pretty', 'Control output processing'),
    ('--print', 'Specify what output should contain'),
    ('--proxy', 'Specify proxy URL'),
    ('--session', 'Create, or reuse and update a session'),
    ('--session-read-only', 'Create or read a session'),
    ('--style', 'Output coloring style'),
    ('--timeout', 'Connection timeout in seconds'),
    ('--verify', 'Set to "no" to skip SSL certificate checking'),
    ('-a', 'Shorthand for --auth'),
    ('-o', 'Shorthand for --output'),
    ('-p', 'Shorthand for --print'),
    ('-s', 'Shorthand for --style'),
]

PRETTY_CHOICES = ('all', 'colors', 'format', 'none')

STYLE_CHOICES = ('algol', 'algol_nu', 'autumn', 'borland', 'bw', 'colorful',
                 'default', 'emacs', 'friendly', 'fruity', 'igor', 'lovelace',
                 'manni', 'monokai', 'murphy', 'native', 'paraiso-dark',
                 'paraiso-light', 'pastie', 'perldoc', 'rrt', 'solarized',
                 'tango', 'trac', 'vim', 'vs', 'xcode')

AUTH_TYPE_CHOICES = ('basic', 'digest')

VERIFY_CHOICES = ('no', 'yes')

OPTION_VALUE_CHOICES = {
    '--auth-type': AUTH_TYPE_CHOICES,
    '--pretty': PRETTY_CHOICES,
    '--style': STYLE_CHOICES,
    '--verify': VERIFY_CHOICES,
    '-p': PRETTY_CHOICES,
    '-s': STYLE_CHOICES,
}

HTTP_METHODS = ('get', 'head', 'post', 'put', 'patch', 'delete', 'options')
