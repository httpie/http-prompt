from pygments.lexer import RegexLexer, bygroups, words, include, combined

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
            (r'(httpie|curl)(\s*)', bygroups(Keyword, Text), 'action'),

            (r'(?i)(get|head|post|put|patch|delete)(\s*)',
             bygroups(Keyword, Text), combined('redir_out', 'urlpath')),

            (r'(exit)(\s*)', bygroups(Keyword, Text), 'end'),
            (r'(help)(\s)*', bygroups(Keyword, Text), 'end'),
            (r'(env)(\s*)', bygroups(Keyword, Text), 'redir_out'),
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

        'concat_mut': [
            (r'$', Text, 'end'),
            (r'\s+', Text),

            # Flag options, such as `--form`, `--json`
            (words(FLAG_OPTIONS, suffix=r'\b'), Name),

            # Options with values, such as `--style=default`, `--pretty all`
            (words(VALUE_OPTIONS, suffix=r'\b'), Name, 'option_op'),

            # Unquoted or value-quoted request mutation,
            # such as `name="John Doe"`, `name=John\ Doe`
            (r'((?:[^\s\'"\\=:]|(?:\\.))+)(:|==|=)',
             bygroups(Name, Operator), 'unquoted_mut'),

            # Full single-quoted request mutation, such as `'name=John Doe'`
            (r"(')((?:[^\r\n'\\=:]|(?:\\.))+)(:|==|=)",
             bygroups(Text, Name, Operator), 'squoted_mut'),

            # Full double-quoted request mutation, such as `"name=John Doe"`
            (r'(")((?:[^\r\n"\\=:]|(?:\\.))+)(:|==|=)',
             bygroups(Text, Name, Operator), 'dquoted_mut')
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
            (r'(?i)(get|head|post|put|patch|delete)(\s*)',
             bygroups(Keyword, Text), combined('redir_out', 'urlpath')),
            include('redir_out'),
            (r'', Text, 'urlpath')
        ],
        'urlpath': [
            (r'https?://([^\s"\'\\]|(\\.))+', String,
             combined('concat_mut', 'redir_out')),

            (r'(")(https?://(?:[^\r\n"\\]|(?:\\.))+)(")',
             bygroups(Text, String, Text),
             combined('concat_mut', 'redir_out')),

            (r'(")(https?://(?:[^\r\n"\\]|(?:\\.))+)',
             bygroups(Text, String)),

            (r"(')(https?://(?:[^\r\n'\\]|(?:\\.))+)(')",
             bygroups(Text, String, Text),
             combined('concat_mut', 'redir_out')),

            (r"(')(https?://(?:[^\r\n'\\]|(?:\\.))+)",
             bygroups(Text, String)),

            (r'(")((?:[^\r\n"\\=:]|(?:\\.))+)(")',
             bygroups(Text, String, Text),
             combined('concat_mut', 'redir_out')),

            (r'(")((?:[^\r\n"\\=:]|(?:\\.))+)', bygroups(Text, String)),

            (r"(')((?:[^\r\n'\\=:]|(?:\\.))+)(')",
             bygroups(Text, String, Text),
             combined('concat_mut', 'redir_out')),

            (r"(')((?:[^\r\n'\\=:]|(?:\\.))+)", bygroups(Text, String)),

            (r'([^\-]([^\s"\'\\=:]|(\\.))+)(\s+|$)',
             String, combined('concat_mut', 'redir_out')),
            (r'', Text, combined('concat_mut', 'redir_out'))
        ],

        'end': [
            (r'\n', Text, 'root')
        ]
    }
