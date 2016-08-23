from pygments.lexer import RegexLexer, bygroups, words, using, include, combined
from pygments.lexers import BashLexer

from pygments.token import Text, String, Keyword, Name, Operator

from . import options as opt


__all__ = ['HttpPromptLexer']


FLAG_OPTIONS = [name for name, _ in opt.FLAG_OPTIONS]
VALUE_OPTIONS = [name for name, _ in opt.VALUE_OPTIONS]


def string_rules(state):
    return [
        (r'(")((?:[^\r\n"\\]|(?:\\.))+)(")',
         bygroups(Text, String, Text), state),

        (r'(")((?:[^\r\n"\\]|(?:\\.))+)', bygroups(Text, String), state),

        (r"(')((?:[^\r\n'\\]|(?:\\.))+)(')",
         bygroups(Text, String, Text), state),

        (r"(')((?:[^\r\n'\\]|(?:\\.))+)", bygroups(Text, String), state),

        (r'([^\s"\'\\]|(\\.))+', String, state)
    ]


class HttpPromptLexer(RegexLexer):

    name = 'HttpPrompt'
    aliases = ['http-prompt']
    filenames = ['*.http-prompt']

    tokens = {
        'root': [
            (r'\s+', Text),
            (r'(cd)(\s*)', bygroups(Keyword, Text), 'cd'),
            (r'(rm)(\s*)', bygroups(Keyword, Text), 'rm_option'),
            (r'(httpie|curl)(\s*)', bygroups(Keyword, Text), 'preview_action'),
            (r'(?i)(get|head|post|put|patch|delete)(\s*)',
             bygroups(Keyword, Text), 'urlpath'),
            (r'exit\s*', Keyword, 'end'),
            (r'help\s*', Keyword, 'end'),
            (r'', Text, 'concat_mut')
        ],

        'cd': string_rules('end'),

        'rm_option': [
            (r'(\-(?:h|o|b|q))(\s*)', bygroups(Name, Text), 'rm_name'),
            (r'(\*)(\s*)', bygroups(Name, Text), 'end')
        ],
        'rm_name': string_rules('end'),

        'shell_command': [
            (r'(`)([^`]*)(`)', bygroups(Text, using(BashLexer), Text)),
        ],
        'concat_mut': [
            (r'$', Text, 'end'),
            (r'\s+', Text),

            # Flag options, such as (--form) and (--json)
            (words(FLAG_OPTIONS, suffix=r'\b'), Name, 'concat_mut'),

            # Options with values, such as (--style=default) and (--pretty all)
            (words(VALUE_OPTIONS, suffix=r'\b'), Name,
             combined('shell_command', 'option_op')),

            include('shell_command'),

            # Unquoted or value-quoted request mutation,
            # such as (name="John Doe") and (name=John\ Doe)
            (r'((?:[^\s\'"\\=:]|(?:\\.))*)(:|==|=)',
             bygroups(Name, Operator), combined('shell_command', 'unquoted_mut')),

            # Full single-quoted request mutation, such as ('name=John Doe')
            (r"(')((?:[^\r\n'\\=:]|(?:\\.))+)(:|==|=)",
             bygroups(Text, Name, Operator), combined('shell_command', 'squoted_mut')),

            # Full double-quoted request mutation, such as ("name=John Doe")
            (r'(")((?:[^\r\n"\\=:]|(?:\\.))+)(:|==|=)',
             bygroups(Text, Name, Operator), combined('shell_command', 'dquoted_mut'))
        ],

        'option_op': [
            (r'(\s+|=)', Operator, 'option_value'),
        ],
        'option_value': string_rules('#pop:2'),

        'unquoted_mut': string_rules('#pop'),
        'squoted_mut': [
            (r"((?:[^\r\n'\\]|(?:\\.))+)(')", bygroups(String, Text), '#pop'),
            (r"([^\r\n'\\]|(\\.))+", String, '#pop')
        ],
        'dquoted_mut': [
            (r'((?:[^\r\n"\\]|(?:\\.))+)(")', bygroups(String, Text), '#pop'),
            (r'([^\r\n"\\]|(\\.))+', String, '#pop')
        ],

        'preview_action': [
            (r'(?i)(get|head|post|put|patch|delete)(\s*)',
             bygroups(Keyword, Text), 'urlpath'),
            (r'', Text, 'urlpath')
        ],
        'urlpath': [
            (r'https?://([^\s"\'\\]|(\\.))+', String, 'concat_mut'),

            (r'(")(https?://(?:[^\r\n"\\]|(?:\\.))+)(")',
             bygroups(Text, String, Text), 'concat_mut'),

            (r'(")(https?://(?:[^\r\n"\\]|(?:\\.))+)', bygroups(Text, String)),

            (r"(')(https?://(?:[^\r\n'\\]|(?:\\.))+)(')",
             bygroups(Text, String, Text), 'concat_mut'),

            (r"(')(https?://(?:[^\r\n'\\]|(?:\\.))+)", bygroups(Text, String)),

            (r'(")((?:[^\r\n"\\=:]|(?:\\.))+)(")',
             bygroups(Text, String, Text), 'concat_mut'),

            (r'(")((?:[^\r\n"\\=:]|(?:\\.))+)', bygroups(Text, String)),

            (r"(')((?:[^\r\n'\\=:]|(?:\\.))+)(')",
             bygroups(Text, String, Text), 'concat_mut'),

            (r"(')((?:[^\r\n'\\=:]|(?:\\.))+)", bygroups(Text, String)),

            (r'([^\-]([^\s"\'\\=:]|(\\.))+)(\s+|$)', String, 'concat_mut'),
            (r'', Text, 'concat_mut')
        ],

        'end': [
            (r'\n', Text, 'root')
        ]
    }
