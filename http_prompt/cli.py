from __future__ import unicode_literals

import click

from prompt_toolkit import prompt
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.contrib.completers import WordCompleter
from pygments.style import Style
from pygments.token import Token
from pygments.styles.default import DefaultStyle


httpie_completer = WordCompleter([
    # Header keys
    'Accept', 'Authorization', 'Content-Type',

    # Header values
    'application/json', 'text/html',

    # Common query parameters
    'page', 'password', 'username',
], ignore_case=True)


class DocumentStyle(Style):
    styles = {
        Token.Menu.Completions.Completion.Current: 'bg:#00aaaa #000000',
        Token.Menu.Completions.Completion: 'bg:#008888 #ffffff',
        Token.Menu.Completions.ProgressButton: 'bg:#003333',
        Token.Menu.Completions.ProgressBar: 'bg:#00aaaa'
    }
    styles.update(DefaultStyle.styles)


@click.command()
@click.argument('url')
def cli(url):
    click.echo("Welcome to HTTP Prompt!")
    history = InMemoryHistory()

    while True:
        try:
            text = prompt('%s> ' % url, completer=httpie_completer,
                          style=DocumentStyle, history=history)
            click.echo("You entered: %s" % text)
        except EOFError:
            break  # Control-D pressed
    click.echo("Goodbye!")
