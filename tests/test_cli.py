from click.testing import CliRunner
from mock import patch

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


def test_without_args():
    result, context = run_and_exit(['http://localhost'])
    assert result.exit_code == 0
    assert context.url == 'http://localhost'
    assert context.options == {}
    assert context.body_params == {}
    assert context.headers == {}
    assert context.querystring_params == {}


def test_incomplete_url1():
    result, context = run_and_exit(['://example.com'])
    assert result.exit_code == 0
    assert context.url == 'http://example.com'
    assert context.options == {}
    assert context.body_params == {}
    assert context.headers == {}
    assert context.querystring_params == {}


def test_incomplete_url2():
    result, context = run_and_exit(['//example.com'])
    assert result.exit_code == 0
    assert context.url == 'http://example.com'
    assert context.options == {}
    assert context.body_params == {}
    assert context.headers == {}
    assert context.querystring_params == {}


def test_incomplete_url3():
    result, context = run_and_exit(['example.com'])
    assert result.exit_code == 0
    assert context.url == 'http://example.com'
    assert context.options == {}
    assert context.body_params == {}
    assert context.headers == {}
    assert context.querystring_params == {}


def test_httpie_options():
    url = 'http://example.com'
    custom_args = '--auth value: name=foo'
    result, context = run_and_exit([url] + custom_args.split())
    assert result.exit_code == 0
    assert context.url == url
    assert context.options == {'--auth': 'value:'}
    assert context.body_params == {'name': 'foo'}
    assert context.headers == {}
    assert context.querystring_params == {}
