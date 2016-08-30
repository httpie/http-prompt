from mock import patch, Mock
import unittest

from http_prompt.printer import Printer
from http_prompt.commandio import CommandIO
from http_prompt.utils import strip_color_codes


class TestCommandIO(unittest.TestCase):

    def setUp(self):
        super(TestCommandIO, self).setUp()
        self.patchers = [
            ('click', patch('http_prompt.printer.click')),
        ]
        for attr_name, patcher in self.patchers:
            setattr(self, attr_name, patcher.start())

        #colored "HTTP" string
        self.test_data = '[38;5;70;01mHTTP[39;00m[38;5;252m'

        attrs = {
            'write.return_value': 3,
            'close.return_value': None,
            'read.return_value': self.test_data
        }
        self.dummyStream = Mock(mode=None, out=None, **attrs)

    def tearDown(self):
        super(TestCommandIO, self).tearDown()
        for _, patcher in self.patchers:
            patcher.stop()

    def test_close(self):
        output = CommandIO(self.dummyStream)
        output.close()
        self.assertTrue(self.dummyStream.close.called)

    def test_write_to_stdout(self):
        output = CommandIO(Printer())
        output.write(self.test_data)

        self.assertTrue(self.click.echo_via_pager.called)
        self.click.style.assert_called_with(
            self.test_data, bg=None, fg=None)
        self.click.echo_via_pager.assert_called_with(
            self.click.style.return_value)

    def test_write(self):
        output = CommandIO(self.dummyStream)
        output.write(self.test_data)

        self.assertTrue(self.dummyStream.write.called)
        args = self.dummyStream.write.call_args[0][0]
        self.assertEqual(strip_color_codes(self.test_data), args)

    def test_write_append(self):
        self.dummyStream.mode = 'a'
        output = CommandIO(self.dummyStream)
        output.write(self.test_data)

        self.assertTrue(self.dummyStream.write.called)
        args = self.dummyStream.write.call_args[0][0]
        self.assertEqual('\n' + strip_color_codes(self.test_data), args)

    def test_read(self):
        output = CommandIO(self.dummyStream)
        output.read()

        self.assertTrue(self.dummyStream.read.called)

    def test_set_output_stream(self):
        stream = Mock()
        output = CommandIO(self.dummyStream)
        output.setOutputStream(stream)

        self.assertEqual(stream, output.out)
