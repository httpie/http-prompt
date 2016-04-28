import unittest

from mock import patch

from http_prompt.context import Context
from http_prompt.execution import execute


class ExecutionTestCase(unittest.TestCase):

    def setUp(self):
        self.patchers = [
            patch('http_prompt.execution.httpie_main'),
            patch('http_prompt.execution.click'),
        ]
        for patcher in self.patchers:
            patcher.start()

        self.context = Context('http://localhost')

    def tearDown(self):
        for patcher in self.patchers:
            patcher.stop()


class TestExecution_cd(ExecutionTestCase):

    def test_single_level(self):
        execute('cd api', self.context)
        self.assertEqual(self.context.url, 'http://localhost/api')

    def test_many_levels(self):
        execute('cd api/v2/movie/50', self.context)
        self.assertEqual(self.context.url, 'http://localhost/api/v2/movie/50')

    def test_change_base(self):
        execute('cd //example.com/api', self.context)
        self.assertEqual(self.context.url, 'http://example.com/api')
