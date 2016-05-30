import six
import unittest

from prompt_toolkit.document import Document

from http_prompt.completer import HttpPromptCompleter
from http_prompt.context import Context


class TestCompleter(unittest.TestCase):

    def setUp(self):
        self.context = Context()
        self.completer = HttpPromptCompleter(self.context)
        self.completer_event = None

    def get_completions(self, command):
        if not isinstance(command, six.text_type):
            command = six.u(command)
        position = len(command)
        completions = self.completer.get_completions(
            Document(text=command, cursor_position=position),
            self.completer_event)
        return [c.text for c in completions]

    def test_header_name(self):
        result = self.get_completions('ctype')
        self.assertEqual(result[0], 'Content-Type')

    def test_header_value(self):
        result = self.get_completions('Content-Type:json')
        self.assertEqual(result[0], 'application/json')

    def test_verify_option(self):
        result = self.get_completions('--vfy')
        self.assertEqual(result[0], '--verify')

    def test_preview_then_action(self):
        result = self.get_completions('httpie po')
        self.assertEqual(result[0], 'post')

    def test_rm_body_param(self):
        self.context.body_params['my_name'] = 'dont_care'
        result = self.get_completions('rm -b ')
        self.assertEqual(result[0], 'my_name')

    def test_rm_querystring_param(self):
        self.context.querystring_params['my_name'] = 'dont_care'
        result = self.get_completions('rm -q ')
        self.assertEqual(result[0], 'my_name')

    def test_rm_header(self):
        self.context.headers['Accept'] = 'dont_care'
        result = self.get_completions('rm -h ')
        self.assertEqual(result[0], 'Accept')

    def test_rm_option(self):
        self.context.options['--form'] = None
        result = self.get_completions('rm -o ')
        self.assertEqual(result[0], '--form')
