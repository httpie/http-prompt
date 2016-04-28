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

    def test_root(self):
        execute('cd /api/v2', self.context)
        self.assertEqual(self.context.url, 'http://localhost/api/v2')

        execute('cd /index.html', self.context)
        self.assertEqual(self.context.url, 'http://localhost/index.html')

    def test_dot_dot(self):
        execute('cd api/v1', self.context)
        self.assertEqual(self.context.url, 'http://localhost/api/v1')

        execute('cd ..', self.context)
        self.assertEqual(self.context.url, 'http://localhost/api')

        execute('cd ../rest/api', self.context)
        self.assertEqual(self.context.url, 'http://localhost/rest/api')

    def test_trailing_slash(self):
        execute('cd api/', self.context)
        self.assertEqual(self.context.url, 'http://localhost/api')

        execute('cd movie/1/', self.context)
        self.assertEqual(self.context.url, 'http://localhost/api/movie/1')
