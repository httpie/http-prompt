import unittest

from mock import patch

from http_prompt.context import Context
from http_prompt.execution import execute


class ExecutionTestCase(unittest.TestCase):

    def setUp(self):
        self.patchers = [
            ('httpie_main', patch('http_prompt.execution.httpie_main')),
            ('click', patch('http_prompt.execution.click')),
        ]
        for attr_name, patcher in self.patchers:
            setattr(self, attr_name, patcher.start())

        self.context = Context('http://localhost')

    def tearDown(self):
        for _, patcher in self.patchers:
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


class TestExecution_rm(ExecutionTestCase):

    def test_header(self):
        self.context.headers['Content-Type'] = 'text/html'
        execute('rm -h Content-Type', self.context)
        self.assertFalse(self.context.headers)

    def test_option(self):
        self.context.options['--form'] = None
        execute('rm -o --form', self.context)
        self.assertFalse(self.context.options)


class TestOptionMutation(ExecutionTestCase):

    def test_long_option_names(self):
        execute('--auth user:pass --form', self.context)
        self.assertEqual(self.context.options, {
            '--form': None,
            '--auth': 'user:pass'
        })


class TestHttpAction(ExecutionTestCase):

    def test_get(self):
        execute('get', self.context)
        self.httpie_main.assert_called_with(['GET', 'http://localhost'])

    def test_post(self):
        execute('post page==1', self.context)
        self.httpie_main.assert_called_with(['POST', 'http://localhost',
                                             'page==1'])


class TestCommandPreview(ExecutionTestCase):

    def test_httpie_without_args(self):
        execute('httpie', self.context)
        self.click.echo.assert_called_with('http http://localhost')

    def test_httpie_with_post(self):
        execute('httpie post name=alice', self.context)
        self.click.echo.assert_called_with(
            'http POST http://localhost name=alice')
        self.assertFalse(self.context.body_params)
