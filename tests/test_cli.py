from mock import patch, ANY

from http_prompt.cli import cli, execute
from click.testing import CliRunner


@patch('http_prompt.cli.prompt')
@patch('http_prompt.cli.execute')
def test_cli_unknown_options(execute_mock, prompt_mock):
    # Emulate a Ctrl+D on first call.
    prompt_mock.side_effect = EOFError
    execute_mock.side_effect = execute

    url = 'http://example.com'
    custom_args = '--auth value: name=foo'

    runner = CliRunner()
    result = runner.invoke(cli, [url] + custom_args.split())

    assert result.exit_code == 0
    execute_mock.assert_called_with(custom_args, ANY)

    context = execute_mock.call_args[0][1]
    assert context.url == url
    assert context.options == {'--auth': 'value:'}
    assert context.body_params == {'name': 'foo'}
