"""Serialization and deserialization of a Context object."""

import json
import os

from six.moves.urllib.parse import urlparse

from . import xdg


# Don't save these attributes of a Context object
EXCLUDED_ATTRS = ['url', 'should_exit']

# Don't save these HTTPie options to avoid collision with user config file
EXCLUDED_OPTIONS = ['--style']


def url_to_context_filename(url):
    r = urlparse(url)
    host = r.hostname
    port = r.port
    if not port:
        port = 443 if r.scheme == 'https' else 80
    return host + '.' + str(port)


def load_context(context):
    """Load a Context object in place from user data directory."""
    dir_path = xdg.get_data_dir('context')
    filename = url_to_context_filename(context.url)
    file_path = os.path.join(dir_path, filename)
    if os.path.exists(file_path):
        with open(file_path) as f:
            json_obj = json.load(f)
        context.load_from_json_obj(json_obj)
        context.should_exit = False


def save_context(context):
    """Save a Context object to user data directory."""
    dir_path = xdg.get_data_dir('context')
    filename = url_to_context_filename(context.url)
    file_path = os.path.join(dir_path, filename)
    json_obj = context.json_obj()

    for name in EXCLUDED_ATTRS:
        json_obj.pop(name, None)

    options = json_obj['options']
    for name in EXCLUDED_OPTIONS:
        options.pop(name, None)

    with open(file_path, 'w') as f:
        json.dump(json_obj, f, indent=4)
