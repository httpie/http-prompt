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


@click.command()
@click.argument('url', default='http://localhost')
def cli(url):
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

    while True:
        try:
            text = prompt('%s> ' % context.url, completer=completer,
                          lexer=lexer, style=style, history=history)
            text = text.strip()
        except EOFError:
            break  # Control-D pressed
        else:
            if text == 'exit':
                break
            if text == '':
                continue
            else:
                execute(text, context)

    click.echo("Goodbye!")
