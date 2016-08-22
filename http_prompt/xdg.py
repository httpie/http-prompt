"""XDG Base Directory Specification.

See:
    https://specifications.freedesktop.org/basedir-spec/basedir-spec-latest.html
    https://github.com/ActiveState/appdirs
"""
import os
import sys

from functools import partial


def _get_dir(envvar_name, default_dir, resource_name=None):
    base_dir = os.getenv(envvar_name) or default_dir
    app_dir = os.path.join(base_dir, 'http-prompt')
    if not os.path.exists(app_dir):
        os.makedirs(app_dir, mode=0o700)

    if resource_name:
        app_dir = os.path.join(app_dir, resource_name)
        if not os.path.exists(app_dir):
            os.mkdir(app_dir)

    return app_dir


if sys.platform == 'win32':  # nocover
    # NOTE: LOCALAPPDATA is not available on Windows XP
    get_tmp_dir = partial(_get_dir, 'TEMP',
                          os.path.expanduser('~/AppData/Local/Temp'))
    get_data_dir = partial(_get_dir, 'LOCALAPPDATA',
                           os.path.expanduser('~/AppData/Local'))
    get_config_dir = partial(_get_dir, 'LOCALAPPDATA',
                             os.path.expanduser('~/AppData/Local'))
else:
    get_tmp_dir = partial(_get_dir, 'TEMP',
                          os.path.expanduser('/tmp/'))
    get_data_dir = partial(_get_dir, 'XDG_DATA_HOME',
                           os.path.expanduser('~/.local/share'))
    get_config_dir = partial(_get_dir, 'XDG_CONFIG_HOME',
                             os.path.expanduser('~/.config'))
