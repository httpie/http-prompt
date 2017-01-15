from pygments.lexer import (RegexLexer, bygroups, words, using, include,
                            combined)
from pygments.lexers import BashLexer

from pygments.token import Text, String, Keyword, Name, Operator

from . import options as opt


__all__ = ['HttpPromptLexer']


FLAG_OPTIONS = [name for name, _ in opt.FLAG_OPTIONS]
VALUE_OPTIONS = [name for name, _ in opt.VALUE_OPTIONS]
HTTP_METHODS = ('get', 'head', 'post', 'put', 'patch', 'delete', 'options')


def string_rules(state):
    return [
        (r'(")((?:[^\r\n"\\]|(?:\\.))+)(")',
         bygroups(Text, String, Text), state),

        (r'(")((?:[^\r\n"\\]|(?:\\.))+)', bygroups(Text, String), state),

        (r"(')((?:[^\r\n'\\]|(?:\\.))+)(')",
         bygroups(Text, String, Text), state),

        (r"(')((?:[^\r\n'\\]|(?:\\.))+)", bygroups(Text, String), state),

        (r'([^\s\'\\]|(\\.))+', String, state)
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
            (r'(httpie|curl)(\s*)', bygroups(Keyword, Text), 'action'),

            (words(HTTP_METHODS, prefix='(?i)', suffix='(?!\S)(\s*)'),
             bygroups(Keyword, Text), combined('redir_out', 'urlpath')),

            (r'(exit)(\s*)', bygroups(Keyword, Text), 'end'),
            (r'(help)(\s)*', bygroups(Keyword, Text), 'end'),
            (r'(env)(\s*)', bygroups(Keyword, Text),
             combined('redir_out', 'pipe')),
            (r'(source)(\s*)', bygroups(Keyword, Text), 'file_path'),
            (r'(exec)(\s*)', bygroups(Keyword, Text), 'file_path'),
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
        'pipe': [
            (r'(\s*)(\|)(.*)', bygroups(Text, Operator, using(BashLexer))),
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
            (r'((?:[^\s\'"\\=:]|(?:\\.))*)(:=|:|==|=)',
             bygroups(Name, Operator),
             combined('shell_command', 'unquoted_mut')),

            # Full single-quoted request mutation, such as ('name=John Doe')
            (r"(')((?:[^\r\n'\\=:]|(?:\\.))+)(:=|:|==|=)",
             bygroups(Text, Name, Operator),
             combined('shell_command', 'squoted_mut')),

            # Full double-quoted request mutation, such as ("name=John Doe")
            (r'(")((?:[^\r\n"\\=:]|(?:\\.))+)(:=|:|==|=)',
             bygroups(Text, Name, Operator),
             combined('shell_command', 'dquoted_mut'))
        ],

        'option_op': [
            (r'(\s+|=)', Operator, 'option_value'),
        ],
        'option_value': string_rules('#pop:2'),
        'file_path': string_rules('end'),
        'redir_out': [
            (r'(?i)(>>?)(\s*)', bygroups(Operator, Text), 'file_path')
        ],

        'unquoted_mut': string_rules('#pop'),
        'squoted_mut': [
            (r"((?:[^\r\n'\\]|(?:\\.))+)(')", bygroups(String, Text), '#pop'),
            (r"([^\r\n'\\]|(\\.))+", String, '#pop')
        ],
        'dquoted_mut': [
            (r'((?:[^\r\n"\\]|(?:\\.))+)(")', bygroups(String, Text), '#pop'),
            (r'([^\r\n"\\]|(\\.))+', String, '#pop')
        ],

        'action': [
            (words(HTTP_METHODS, prefix='(?i)', suffix='(\s*)'),
             bygroups(Keyword, Text),
             combined('redir_out', 'pipe', 'urlpath')),
            (r'', Text, combined('redir_out', 'pipe', 'urlpath'))
        ],
        'urlpath': [
            (r'https?://([^\s"\'\\]|(\\.))+', String,
             combined('concat_mut', 'redir_out', 'pipe')),

            (r'(")(https?://(?:[^\r\n"\\]|(?:\\.))+)(")',
             bygroups(Text, String, Text),
             combined('concat_mut', 'redir_out', 'pipe')),

            (r'(")(https?://(?:[^\r\n"\\]|(?:\\.))+)',
             bygroups(Text, String)),

            (r"(')(https?://(?:[^\r\n'\\]|(?:\\.))+)(')",
             bygroups(Text, String, Text),
             combined('concat_mut', 'redir_out', 'pipe')),

            (r"(')(https?://(?:[^\r\n'\\]|(?:\\.))+)",
             bygroups(Text, String)),

            (r'(")((?:[^\r\n"\\=:]|(?:\\.))+)(")',
             bygroups(Text, String, Text),
             combined('concat_mut', 'redir_out', 'pipe')),

            (r'(")((?:[^\r\n"\\=:]|(?:\\.))+)', bygroups(Text, String)),

            (r"(')((?:[^\r\n'\\=:]|(?:\\.))+)(')",
             bygroups(Text, String, Text),
             combined('concat_mut', 'redir_out', 'pipe')),

            (r"(')((?:[^\r\n'\\=:]|(?:\\.))+)", bygroups(Text, String)),

            (r'([^\-](?:[^\s"\'\\=:]|(\\.))+)(\s+|$)',
             bygroups(String, Text),
             combined('concat_mut', 'redir_out', 'pipe')),

            (r'', Text,
             combined('concat_mut', 'redir_out', 'pipe'))
        ],

        'end': [
            (r'\n', Text, 'root')
        ]
    }
