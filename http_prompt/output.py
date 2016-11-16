import sys

import click
import six


class Printer(object):
    """Wrap click.echo_via_pager() so it accepts binary data."""

    def write(self, data):
        if isinstance(data, six.binary_type):
            data = data.decode('utf-8')

        # echo_via_pager() already appends a '\n' at the end of text,
        # so we use rstrip() to remove extra newlines (#89)
        click.echo_via_pager(data.rstrip())

    def flush(self):
        pass

    def close(self):
        pass

    def isatty(self):
        return True

    def fileno(self):
        return sys.stdout.fileno()


class TextWriter(object):
    """Wrap a file-like object, opened with 'wb' or 'ab', so it accepts text
    data.
    """
    def __init__(self, fp):
        self.fp = fp

    def write(self, data):
        if isinstance(data, six.text_type):
            data = data.encode('utf-8')
        self.fp.write(data)

    def flush(self):
        self.fp.flush()

    def close(self):
        self.fp.close()

    def isatty(self):
        return self.fp.isatty()

    def fileno(self):
        return self.fp.fileno()
