import os
import sys


def get_http_prompt_path():
    """Get the path to http-prompt executable."""
    python_dir = os.path.dirname(sys.executable)
    bin_name = 'http-prompt'
    if sys.platform == 'win32':
        bin_name += '.exe'

    bin_path = os.path.join(python_dir, bin_name)
    if os.path.exists(bin_path):
        return bin_path

    # Try 'Scripts' directory (for Windows)
    bin_path = os.path.join(python_dir, 'Scripts', bin_name)
    if os.path.exists(bin_path):
        return bin_path

    raise OSError("could not locate http-prompt executable, "
                  "Python directory: %s" % python_dir)
