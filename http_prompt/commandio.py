import sys
import six

from .printer import Printer
from .utils import strip_color_codes


class CommandIO():

    def __init__(self, stream=sys.stdout):
        self.out = stream

    def close(self):
        return self.out.close()

    def write(self, data):
        if self.out is not Printer:
            data = strip_color_codes(data)

        if hasattr(
            self.out,
            'mode') and isinstance(
            self.out.mode,
         six.string_types) and self.out.mode.find('a') != -1:
            data = '\n' + data

        return self.out.write(data)

    def read(self):
        return self.out.read()

    def setOutputStream(self, stream):
        self.out = stream
