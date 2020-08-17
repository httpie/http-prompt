"""Functions that deal with the user configuration."""

import os
import shutil

from . import defaultconfig
from . import xdg


def get_user_config_path():
    """Get the path to the user config file."""
    return os.path.join(xdg.get_config_dir(), 'config.py')


def initialize():
    """Initialize a default config file if it doesn't exist yet.

    Returns:
        tuple: A tuple of (copied, dst_path). `copied` is a bool indicating if
            this function created the default config file. `dst_path` is the
            path of the user config file.
    """
    dst_path = get_user_config_path()
    copied = False
    if not os.path.exists(dst_path):
        src_path = os.path.join(os.path.dirname(__file__), 'defaultconfig.py')
        shutil.copyfile(src_path, dst_path)
        copied = True
    return copied, dst_path


def _module_to_dict(module):
    attrs = {}
    attr_names = filter(lambda n: not n.startswith('_'), dir(module))
    for name in attr_names:
        value = getattr(module, name)
        attrs[name] = value
    return attrs


def load_default():
    """Return default config as a dict."""
    return _module_to_dict(defaultconfig)


def load_user():
    """Read user config file and return it as a dict."""
    config_path = get_user_config_path()
    config = {}

    # TODO: This may be overkill and too slow just for reading a config file
    with open(config_path) as f:
        code = compile(f.read(), config_path, 'exec')
    exec(code, config)

    keys = list(config.keys())
    for k in keys:
        if k.startswith('_'):
            del config[k]

    return config


def load():
    """Read default and user config files and return them as a dict."""
    config = load_default()
    config.update(load_user())
    return config
