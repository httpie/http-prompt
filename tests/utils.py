import os
import sys


def get_http_prompt_path():
    """Get the path to http-prompt executable."""
    bin_name = 'http-prompt'
    if sys.platform == 'win32':
        bin_name += '.exe'
    return os.path.join(os.path.dirname(sys.executable), bin_name)
