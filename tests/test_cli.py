import os

from click.testing import CliRunner
from mock import patch

from .base import TempAppDirTestCase
from http_prompt import xdg
from http_prompt.cli import cli, execute


@patch('http_prompt.cli.prompt')
@patch('http_prompt.cli.execute')
def run_and_exit(args, execute_mock, prompt_mock):
    """Run http-prompt executable and exit immediately."""
    # Emulate a Ctrl+D on first call.
    prompt_mock.side_effect = EOFError
    execute_mock.side_effect = execute

    runner = CliRunner()
    result = runner.invoke(cli, args)

    context = execute_mock.call_args[0][1]
    return result, context


class TestCli(TempAppDirTestCase):

    def test_without_args(self):
        result, context = run_and_exit(['http://localhost'])
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(context.url, 'http://localhost')
        self.assertEqual(context.options, {})
        self.assertEqual(context.body_params, {})
        self.assertEqual(context.headers, {})
        self.assertEqual(context.querystring_params, {})

    def test_incomplete_url1(self):
        result, context = run_and_exit(['://example.com'])
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(context.url, 'http://example.com')
        self.assertEqual(context.options, {})
        self.assertEqual(context.body_params, {})
        self.assertEqual(context.headers, {})
        self.assertEqual(context.querystring_params, {})

    def test_incomplete_url2(self):
        result, context = run_and_exit(['//example.com'])
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(context.url, 'http://example.com')
        self.assertEqual(context.options, {})
        self.assertEqual(context.body_params, {})
        self.assertEqual(context.headers, {})
        self.assertEqual(context.querystring_params, {})

    def test_incomplete_url3(self):
        result, context = run_and_exit(['example.com'])
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(context.url, 'http://example.com')
        self.assertEqual(context.options, {})
        self.assertEqual(context.body_params, {})
        self.assertEqual(context.headers, {})
        self.assertEqual(context.querystring_params, {})

    def test_httpie_oprions(self):
        url = 'http://example.com'
        custom_args = '--auth value: name=foo'
        result, context = run_and_exit([url] + custom_args.split())
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(context.url, 'http://example.com')
        self.assertEqual(context.options, {'--auth': 'value:'})
        self.assertEqual(context.body_params, {'name': 'foo'})
        self.assertEqual(context.headers, {})
        self.assertEqual(context.querystring_params, {})

    def test_persistent_context(self):
        result, context = run_and_exit(['//example.com', 'name=bob', 'id==10'])
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(context.url, 'http://example.com')
        self.assertEqual(context.options, {})
        self.assertEqual(context.body_params, {'name': 'bob'})
        self.assertEqual(context.headers, {})
        self.assertEqual(context.querystring_params, {'id': '10'})

        result, context = run_and_exit(['//example.com', 'sex=M'])
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(context.url, 'http://example.com')
        self.assertEqual(context.options, {})
        self.assertEqual(context.body_params, {'name': 'bob', 'sex': 'M'})
        self.assertEqual(context.headers, {})
        self.assertEqual(context.querystring_params, {'id': '10'})

    def test_config_file(self):
        # Config file is not there at the beginning
        config_path = os.path.join(xdg.get_config_dir(), 'config.py')
        self.assertFalse(os.path.exists(config_path))

        # After user runs it for the first time, a default config file should
        # be created
        result, context = run_and_exit(['//example.com'])
        self.assertEqual(result.exit_code, 0)
        self.assertTrue(os.path.exists(config_path))
