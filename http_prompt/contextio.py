"""Serialization and deserialization of a Context object."""

import os

from . import xdg
from .context.transform import format_to_http_prompt
from .execution import execute


# Don't save these HTTPie options to avoid collision with user config file
EXCLUDED_OPTIONS = ['--style']

# Filename the current environment context will be saved to
CONTEXT_FILENAME = 'context.hp'


def _get_context_filepath():
    dir_path = xdg.get_data_dir()
    return os.path.join(dir_path, CONTEXT_FILENAME)


def load_context(context):
    """Load a Context object in place from user data directory."""
    file_path = _get_context_filepath()
    if os.path.exists(file_path):
        with open(file_path) as f:
            for line in f:
                execute(line, context)


def save_context(context):
    """Save a Context object to user data directory."""
    file_path = _get_context_filepath()
    content = format_to_http_prompt(context, excluded_options=EXCLUDED_OPTIONS)
    with open(file_path, 'w') as f:
        f.write(content)
