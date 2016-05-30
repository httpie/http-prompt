import sys

import pexpect
import pytest

from .utils import get_http_prompt_path


@pytest.mark.skipif(sys.platform == 'win32',
                    reason="pexpect doesn't work well on Windows")
@pytest.mark.slow
def test_interaction():
    bin_path = get_http_prompt_path()
    child = pexpect.spawn(bin_path)

    # TODO: Test more interaction

    child.sendline('exit')
    child.expect_exact('Goodbye!', timeout=20)
    child.close()
