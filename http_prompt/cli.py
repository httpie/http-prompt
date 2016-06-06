import json
import os
import shutil

import click

from six.moves.urllib.parse import urlparse
from prompt_toolkit import prompt
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.layout.lexers import PygmentsLexer
from prompt_toolkit.styles.from_pygments import style_from_pygments
from pygments.styles import get_style_by_name

from . import __version__
from . import xdg
from .completer import HttpPromptCompleter
from .context import Context
from .execution import execute
from .lexer import HttpPromptLexer


def fix_incomplete_url(url):
    if url.startswith('s://') or url.startswith('://'):
        url = 'http' + url
    elif url.startswith('//'):
        url = 'http:' + url
    elif not url.startswith('http://') and not url.startswith('https://'):
        url = 'http://' + url
    return url


def load_context(context):
    dir_path = xdg.get_data_dir('context')
    host = urlparse(context.url).hostname
    file_path = os.path.join(dir_path, host)
    if os.path.exists(file_path):
        with open(file_path) as f:
            json_obj = json.load(f)
        context.load_from_json_obj(json_obj)
        context.should_exit = False


def save_context(context):
    dir_path = xdg.get_data_dir('context')
    host = urlparse(context.url).hostname
    file_path = os.path.join(dir_path, host)
    json_obj = context.json_obj()
    with open(file_path, 'w') as f:
        json.dump(json_obj, f, indent=4)


def init_config_file(config_path):
    src_path = os.path.join(os.path.dirname(__file__), 'default_config.py')
    shutil.copyfile(src_path, config_path)


def load_config_file(config_path):
    with open(config_path) as f:
        content = f.read()
    config = {}
    code = compile(content, config_path, 'exec')
    exec(code, config)
    return config


@click.command(context_settings=dict(
    ignore_unknown_options=True,
))
@click.argument('url', default='http://localhost')
@click.argument('http_options', nargs=-1, type=click.UNPROCESSED)
@click.version_option(message='%(version)s')
def cli(url, http_options):
    click.echo('Version: %s' % __version__)

    config_path = os.path.join(xdg.get_config_dir(), 'config.py')
    if not os.path.exists(config_path):
        init_config_file(config_path)
        click.echo('Config file not found. Initialized a default one: %s' %
                   config_path)

    config = load_config_file(config_path)

    # Override pager/less options
    os.environ['PAGER'] = config['pager']
    os.environ['LESS'] = '-RXF'

    url = fix_incomplete_url(url)
    context = Context(url)
    load_context(context)

    if 'output_style' in config:
        context.options['--style'] = config['output_style']

        if context.options['--style'] == 'monokai':
            # HTTPie default style is monokai, no need to store
            del context.options['--style']

    # For prompt-toolkit
    history = InMemoryHistory()
    lexer = PygmentsLexer(HttpPromptLexer)
    completer = HttpPromptCompleter(context)
    style = style_from_pygments(get_style_by_name(config['command_style']))

    # Execute default http options.
    execute(' '.join(http_options), context)
    save_context(context)

    while True:
        try:
            text = prompt('%s> ' % context.url, completer=completer,
                          lexer=lexer, style=style, history=history)
        except EOFError:
            break  # Control-D pressed
        else:
            execute(text, context)
            save_context(context)
            if context.should_exit:
                break

    click.echo("Goodbye!")
