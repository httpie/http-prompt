import os
import sys


def get_http_prompt_path():
    """Get the path to http-prompt executable."""
    bin_name = 'http-prompt'
    if sys.platform == 'win32':
        bin_name += '.exe'
    bin_path = os.path.join(os.path.dirname(sys.executable), bin_name)
    if os.path.exists(bin_path):
        return bin_path
    return bin_name  # Try PATH
