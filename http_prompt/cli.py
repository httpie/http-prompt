import click

from prompt_toolkit import prompt
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.layout.lexers import PygmentsLexer
from prompt_toolkit.styles.from_pygments import style_from_pygments
from pygments.styles import get_style_by_name

from .completer import HttpPromptCompleter
from .context import Context
from .execution import execute
from .lexer import HttpPromptLexer


@click.command()
@click.argument('url')
def cli(url):
    click.echo("Welcome to HTTP Prompt!")
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
        except EOFError:
            break  # Control-D pressed
        else:
            execute(text, context)

    click.echo("Goodbye!")
