import click

from prompt_toolkit import prompt
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.layout.lexers import PygmentsLexer
from prompt_toolkit.styles import PygmentsStyle
from pygments.token import Token

from .completer import HttpPromptCompleter
from .context import Context
from .execution import execute
from .lexer import HttpPromptLexer


@click.command()
@click.argument('url')
def cli(url):
    click.echo("Welcome to HTTP Prompt!")

    # For prompt-toolkit
    history = InMemoryHistory()
    lexer = PygmentsLexer(HttpPromptLexer)
    completer = HttpPromptCompleter()
    style = PygmentsStyle.from_defaults({
        Token.Operator:       '#33aaaa bold',
        Token.Number:         '#aa3333 bold',
        Token.TrailingInput: 'bg:#662222 #ffffff'
    })

    context = Context(url)

    while True:
        try:
            text = prompt('%s> ' % context.url, completer=completer,
                          lexer=lexer, style=style, history=history)
        except EOFError:
            break  # Control-D pressed
        else:
            execute(text, context)

    click.echo("Goodbye!")
