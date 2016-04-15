from pygments.lexer import RegexLexer
from pygments.token import Token


class HttpPromptLexer(RegexLexer):
    name = 'HttpPrompt'
    aliases = ['http-prompt']
    filenames = ['*.http-prompt']

    tokens = {
        'root': [
            (r'.*\n', Token.Text)
        ]
    }
