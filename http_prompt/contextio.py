"""Serialization and deserialization of a Context object."""

import json
import os

from six.moves.urllib.parse import urlparse

from . import xdg


# Don't save these HTTPie options to avoid collision with user config file
EXCLUDED_OPTIONS = ['--style']


def load_context(context):
    """Load a Context object in place from user data directory."""
    dir_path = xdg.get_data_dir('context')
    host = urlparse(context.url).hostname
    file_path = os.path.join(dir_path, host)
    if os.path.exists(file_path):
        with open(file_path) as f:
            json_obj = json.load(f)
        context.load_from_json_obj(json_obj)
        context.should_exit = False


def save_context(context):
    """Save a Context object to user data directory."""
    dir_path = xdg.get_data_dir('context')
    host = urlparse(context.url).hostname
    file_path = os.path.join(dir_path, host)
    json_obj = context.json_obj()

    options = json_obj['options']
    for name in EXCLUDED_OPTIONS:
        options.pop(name, None)

    with open(file_path, 'w') as f:
        json.dump(json_obj, f, indent=4)
