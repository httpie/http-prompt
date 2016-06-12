import os

import click

from httpie.plugins import FormatterPlugin  # noqa, avoid cyclic import
from httpie.output.formatters.colors import Solarized256Style
from prompt_toolkit import prompt
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.layout.lexers import PygmentsLexer
from prompt_toolkit.styles.from_pygments import style_from_pygments
from pygments.styles import get_style_by_name
from pygments.util import ClassNotFound

from . import __version__
from . import config
from .completer import HttpPromptCompleter
from .context import Context
from .contextio import load_context, save_context
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


@click.command(context_settings=dict(
    ignore_unknown_options=True,
))
@click.argument('url', default='http://localhost')
@click.argument('http_options', nargs=-1, type=click.UNPROCESSED)
@click.version_option(message='%(version)s')
def cli(url, http_options):
    click.echo('Version: %s' % __version__)

    copied, config_path = config.initialize()
    if copied:
        click.echo('Config file not found. Initialized a new one: %s' %
                   config_path)

    cfg = config.load()

    # Override pager/less options
    os.environ['PAGER'] = cfg['pager']
    os.environ['LESS'] = '-RXF'

    url = fix_incomplete_url(url)
    context = Context(url)
    load_context(context)

    output_style = cfg.get('output_style')
    if output_style:
        context.options['--style'] = output_style

    # For prompt-toolkit
    history = InMemoryHistory()
    lexer = PygmentsLexer(HttpPromptLexer)
    completer = HttpPromptCompleter(context)
    try:
        style = get_style_by_name(cfg['command_style'])
    except ClassNotFound:
        style = style_from_pygments(Solarized256Style)
    else:
        style = style_from_pygments(style)

    # Execute default HTTPie options
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
