import os

import click

from prompt_toolkit import prompt
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.layout.lexers import PygmentsLexer
from prompt_toolkit.styles.from_pygments import style_from_pygments
from pygments.styles import get_style_by_name

from . import __version__
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


@click.command(context_settings=dict(
    ignore_unknown_options=True,
))
@click.argument('url', default='http://localhost')
@click.argument('http_options', nargs=-1, type=click.UNPROCESSED)
@click.version_option(message='%(version)s')
def cli(url, http_options):
    click.echo('Version: %s' % __version__)

    # Override less options
    os.environ['LESS'] = '-RXF'

    url = fix_incomplete_url(url)
    context = Context(url)

    # For prompt-toolkit
    history = InMemoryHistory()
    lexer = PygmentsLexer(HttpPromptLexer)
    completer = HttpPromptCompleter(context)
    style = style_from_pygments(get_style_by_name('monokai'))

    # Execute default http options.
    execute(' '.join(http_options), context)

    while True:
        try:
            text = prompt('%s> ' % context.url, completer=completer,
                          lexer=lexer, style=style, history=history)
        except EOFError:
            break  # Control-D pressed
        else:
            execute(text, context)
            if context.should_exit:
                break

    click.echo("Goodbye!")
