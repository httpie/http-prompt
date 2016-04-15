import click

from prompt_toolkit import prompt
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.layout.lexers import PygmentsLexer
from prompt_toolkit.styles import PygmentsStyle
from pygments.token import Token

from .completer import HttpPromptCompleter
from .lexer import HttpPromptLexer

# command = action | header | querystring
# action = "GET" | "POST"
# header = header_name ":" header_value
# header_name = ...
# header_value = ...
# querystring = param_name "==" param_value


@click.command()
@click.argument('url')
def cli(url):
    click.echo("Welcome to HTTP Prompt!")

    history = InMemoryHistory()
    lexer = PygmentsLexer(HttpPromptLexer)
    completer = HttpPromptCompleter()

    style = PygmentsStyle.from_defaults({
        Token.Operator:       '#33aaaa bold',
        Token.Number:         '#aa3333 bold',
        Token.TrailingInput: 'bg:#662222 #ffffff'
    })

    while True:
        try:
            text = prompt('%s> ' % url, completer=completer, lexer=lexer,
                          style=style, history=history)
            click.echo("You entered: %s" % text)
        except EOFError:
            break  # Control-D pressed
    click.echo("Goodbye!")
