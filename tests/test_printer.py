from mock import patch
import unittest

from http_prompt.printer import Printer


class TestPrinter(unittest.TestCase):

    def setUp(self):
        super(TestPrinter, self).setUp()
        self.patchers = [
            ('click', patch('http_prompt.printer.click')),
        ]
        for attr_name, patcher in self.patchers:
            setattr(self, attr_name, patcher.start())

    def tearDown(self):
        super(TestPrinter, self).tearDown()
        for _, patcher in self.patchers:
            patcher.stop()

    def test_write_err(self):
        err_message = 'error message'
        printer = Printer(fg='red', bg='white', err=True)
        printer.write(err_message)

        self.click.secho.assert_called_with(
            err_message, fg='red', bg='white', err=True, nl=True)

    def test_write(self):
        data = 'data string'
        printer = Printer(fg='red', bg='white')
        printer.write(data)

        self.click.style.assert_called_with(
            data, fg='red', bg='white')
        self.click.echo_via_pager.assert_called_with(
            self.click.style.return_value)
