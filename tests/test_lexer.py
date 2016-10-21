import unittest

from pygments.token import Keyword, String, Text, Error, Name, Operator, Literal

from http_prompt.lexer import HttpPromptLexer


class LexerTestCase(unittest.TestCase):

    def setUp(self):
        self.lexer = HttpPromptLexer()

    def get_tokens(self, text):
        tokens = []
        for ttype, value in self.lexer.get_tokens(text):
            if value.strip():
                tokens.append((ttype, value))
        return tokens


class TestLexer_cd(LexerTestCase):

    def test_simple(self):
        self.assertEqual(self.get_tokens('cd api/v1'), [
            (Keyword, 'cd'),
            (String, 'api/v1')
        ])

    def test_double_quoted(self):
        self.assertEqual(self.get_tokens('cd "api/v 1"'), [
            (Keyword, 'cd'),
            (Text, '"'),
            (String, 'api/v 1'),
            (Text, '"')
        ])

    def test_single_quoted(self):
        self.assertEqual(self.get_tokens("cd 'api/v 1'"), [
            (Keyword, 'cd'),
            (Text, "'"),
            (String, 'api/v 1'),
            (Text, "'")
        ])

    def test_escape(self):
        self.assertEqual(self.get_tokens(r"cd api/v\ 1"), [
            (Keyword, 'cd'),
            (String, r'api/v\ 1')
        ])

    def test_second_path(self):
        self.assertEqual(self.get_tokens(r"cd api v1"), [
            (Keyword, 'cd'),
            (String, 'api'),
            (Error, 'v'),
            (Error, '1')
        ])

    def test_leading_trailing_spaces(self):
        self.assertEqual(self.get_tokens('   cd   api/v1  '), [
            (Keyword, 'cd'),
            (String, 'api/v1')
        ])


class TestLexer_env(LexerTestCase):

    def test_env_simple(self):
        self.assertEqual(self.get_tokens('env'), [
            (Keyword, 'env'),
        ])

    def test_env_with_spaces(self):
        self.assertEqual(self.get_tokens('   env    '), [
            (Keyword, 'env'),
        ])

    def test_env_write(self):
        self.assertEqual(self.get_tokens('env > /tmp/file.txt'), [
            (Keyword, 'env'), (Operator, '>'),
            (String, '/tmp/file.txt')
        ])

    def test_env_append(self):
        self.assertEqual(self.get_tokens('env >> /tmp/file.txt'), [
            (Keyword, 'env'), (Operator, '>>'),
            (String, '/tmp/file.txt')
        ])

    def test_env_write_quoted_filename(self):
        self.assertEqual(self.get_tokens('env > "/tmp/my file.txt"'), [
            (Keyword, 'env'), (Operator, '>'),
            (Text, '"'), (String, '/tmp/my file.txt'), (Text, '"')
        ])

    def test_env_append_escaped_filename(self):
        self.assertEqual(self.get_tokens(r'env >> /tmp/my\ file.txt'), [
            (Keyword, 'env'), (Operator, '>>'),
            (String, r'/tmp/my\ file.txt')
        ])

    def test_env_pipe(self):
        self.assertEqual(self.get_tokens('env | grep name'), [
            (Keyword, 'env'), (Operator, '|'),
            (Text, 'grep'), (Text, 'name')
        ])


class TestLexer_rm(LexerTestCase):

    def test_header(self):
        self.assertEqual(self.get_tokens('rm -h Accept'), [
            (Keyword, 'rm'),
            (Name, '-h'),
            (String, 'Accept')
        ])

    def test_header_escaped(self):
        self.assertEqual(self.get_tokens(r'rm -h Custom\ Header'), [
            (Keyword, 'rm'),
            (Name, '-h'),
            (String, r'Custom\ Header')
        ])

    def test_querystring(self):
        self.assertEqual(self.get_tokens('rm -q page'), [
            (Keyword, 'rm'),
            (Name, '-q'),
            (String, 'page')
        ])

    def test_querystring_double_quoted(self):
        self.assertEqual(self.get_tokens('rm -q "page size"'), [
            (Keyword, 'rm'),
            (Name, '-q'),
            (Text, '"'),
            (String, 'page size'),
            (Text, '"')
        ])

    def test_body_param(self):
        self.assertEqual(self.get_tokens('rm -b name'), [
            (Keyword, 'rm'),
            (Name, '-b'),
            (String, 'name')
        ])

    def test_body_param_single_quoted(self):
        self.assertEqual(self.get_tokens("rm -b 'first name'"), [
            (Keyword, 'rm'),
            (Name, '-b'),
            (Text, "'"),
            (String, 'first name'),
            (Text, "'")
        ])

    def test_option(self):
        self.assertEqual(self.get_tokens('rm -o --json'), [
            (Keyword, 'rm'),
            (Name, '-o'),
            (String, '--json')
        ])

    def test_reset(self):
        self.assertEqual(self.get_tokens('rm *'), [
            (Keyword, 'rm'),
            (Name, '*')
        ])

    def test_option_leading_trailing_spaces(self):
        self.assertEqual(self.get_tokens('  rm  -o    --json   '), [
            (Keyword, 'rm'),
            (Name, '-o'),
            (String, '--json')
        ])

    def test_invalid_type(self):
        self.assertEqual(self.get_tokens('rm -a foo'), [
            (Keyword, 'rm'),
            (Error, '-'), (Error, 'a'),
            (Error, 'f'), (Error, 'o'), (Error, 'o')
        ])


class TestLexer_help(LexerTestCase):

    def test_help_simple(self):
        self.assertEqual(self.get_tokens('help'), [
            (Keyword, 'help')
        ])

    def test_help_with_spaces(self):
        self.assertEqual(self.get_tokens('  help   '), [
            (Keyword, 'help')
        ])


class TestLexer_source(LexerTestCase):

    def test_source_simple_filename(self):
        self.assertEqual(self.get_tokens('source file.txt'), [
            (Keyword, 'source'), (String, 'file.txt')
        ])

    def test_source_with_spaces(self):
        self.assertEqual(self.get_tokens('  source    file.txt    '), [
            (Keyword, 'source'), (String, 'file.txt')
        ])

    def test_source_quoted_filename(self):
        self.assertEqual(self.get_tokens("source '/tmp/my file.txt'"), [
            (Keyword, 'source'),
            (Text, "'"), (String, '/tmp/my file.txt'), (Text, "'")
        ])

    def test_source_escaped_filename(self):
        self.assertEqual(self.get_tokens(r"source /tmp/my\ file.txt"), [
            (Keyword, 'source'), (String, r'/tmp/my\ file.txt')
        ])


class TestLexer_exec(LexerTestCase):

    def test_exec_simple_filename(self):
        self.assertEqual(self.get_tokens('exec file.txt'), [
            (Keyword, 'exec'), (String, 'file.txt')
        ])

    def test_exec_with_spaces(self):
        self.assertEqual(self.get_tokens('  exec    file.txt    '), [
            (Keyword, 'exec'), (String, 'file.txt')
        ])

    def test_exec_quoted_filename(self):
        self.assertEqual(self.get_tokens("exec '/tmp/my file.txt'"), [
            (Keyword, 'exec'),
            (Text, "'"), (String, '/tmp/my file.txt'), (Text, "'")
        ])

    def test_exec_escaped_filename(self):
        self.assertEqual(self.get_tokens(r"exec /tmp/my\ file.txt"), [
            (Keyword, 'exec'), (String, r'/tmp/my\ file.txt')
        ])


class TestLexer_exit(LexerTestCase):

    def test_exit_simple(self):
        self.assertEqual(self.get_tokens('exit'), [
            (Keyword, 'exit')
        ])

    def test_exit_with_spaces(self):
        self.assertEqual(self.get_tokens('  exit   '), [
            (Keyword, 'exit')
        ])


class TestLexerPreview(LexerTestCase):

    def test_httpie_without_action(self):
        cmd = 'httpie http://example.com name=jack'
        self.assertEqual(self.get_tokens(cmd), [
            (Keyword, 'httpie'),
            (String, 'http://example.com'),
            (Name, 'name'), (Operator, '='), (String, 'jack')
        ])

    def test_httpie_without_action_and_url(self):
        cmd = 'httpie name=jack Accept:*/*'
        self.assertEqual(self.get_tokens(cmd), [
            (Keyword, 'httpie'),
            (Name, 'name'), (Operator, '='), (String, 'jack'),
            (Name, 'Accept'), (Operator, ':'), (String, '*/*')
        ])

    def test_httpie_absolute_url(self):
        cmd = 'httpie post http://example.com name=jack'
        self.assertEqual(self.get_tokens(cmd), [
            (Keyword, 'httpie'), (Keyword, 'post'),
            (String, 'http://example.com'),
            (Name, 'name'), (Operator, '='), (String, 'jack')
        ])

    def test_httpie_option_first(self):
        self.assertEqual(self.get_tokens('httpie post --form name=jack'), [
            (Keyword, 'httpie'), (Keyword, 'post'),
            (Name, '--form'),
            (Name, 'name'), (Operator, '='), (String, 'jack')
        ])

    def test_httpie_body_param_first(self):
        self.assertEqual(self.get_tokens('httpie post name=jack --form'), [
            (Keyword, 'httpie'), (Keyword, 'post'),
            (Name, 'name'), (Operator, '='), (String, 'jack'),
            (Name, '--form')
        ])


class TestShellCode(LexerTestCase):

    def test_unquoted_querystring(self):
        self.assertEqual(self.get_tokens('`echo name`==john'), [
            (Text, '`'),
            (Name.Builtin, 'echo'),
            (Text, 'name'),
            (Text, '`'),
            (Operator, '=='),
            (String, 'john')
        ])
        self.assertEqual(self.get_tokens('name==`echo john`'), [
            (Name, 'name'),
            (Operator, '=='),
            (Text, '`'),
            (Name.Builtin, 'echo'),
            (Text, 'john'),
            (Text, '`')
        ])

    def test_unquoted_bodystring(self):
        self.assertEqual(self.get_tokens('`echo name`=john'), [
            (Text, '`'),
            (Name.Builtin, 'echo'),
            (Text, 'name'),
            (Text, '`'),
            (Operator, '='),
            (String, 'john')
        ])
        self.assertEqual(self.get_tokens('name=`echo john`'), [
            (Name, 'name'),
            (Operator, '='),
            (Text, '`'),
            (Name.Builtin, 'echo'),
            (Text, 'john'),
            (Text, '`')
        ])

    def test_header_option_value(self):
        self.assertEqual(self.get_tokens('Accept:`echo "application/json"`'), [
            (Name, 'Accept'),
            (Operator, ':'),
            (Text, '`'),
            (Name.Builtin, 'echo'),
            (String.Double, '"application/json"'),
            (Text, '`'),
        ])

    def test_httpie_body_param(self):
        self.assertEqual(self.get_tokens('httpie post name=`echo john`'), [
            (Keyword, 'httpie'),
            (Keyword, 'post'),
            (Name, 'name'),
            (Operator, '='),
            (Text, '`'),
            (Name.Builtin, 'echo'),
            (Text, 'john'),
            (Text, '`'),
        ])

    def test_httpie_post_pipe(self):
        self.assertEqual(self.get_tokens('httpie post | tee "/tmp/test"'), [
            (Keyword, 'httpie'),
            (Keyword, 'post'),
            (Operator, '|'),
            (Text, 'tee'),
            (String.Double, '"/tmp/test"'),
        ])

    def test_post_pipe(self):
        self.assertEqual(self.get_tokens('post | tee "/tmp/test"'), [
            (Keyword, 'post'),
            (Operator, '|'),
            (Text, 'tee'),
            (String.Double, '"/tmp/test"'),
        ])


class TestLexerPreviewRedirection(LexerTestCase):

    def test_httpie_write(self):
        self.assertEqual(self.get_tokens('httpie > file.txt'), [
            (Keyword, 'httpie'),
            (Operator, '>'), (String, 'file.txt')
        ])

    def test_httpie_write_without_spaces(self):
        self.assertEqual(self.get_tokens('httpie>file.txt'), [
            (Keyword, 'httpie'),
            (Operator, '>'), (String, 'file.txt')
        ])

    def test_httpie_append(self):
        self.assertEqual(self.get_tokens('httpie >> file.txt'), [
            (Keyword, 'httpie'),
            (Operator, '>>'), (String, 'file.txt')
        ])

    def test_httpie_append_without_spaces(self):
        self.assertEqual(self.get_tokens('httpie>>file.txt'), [
            (Keyword, 'httpie'),
            (Operator, '>>'), (String, 'file.txt')
        ])

    def test_httpie_write_with_post_param(self):
        self.assertEqual(self.get_tokens('httpie post name=jack > file.txt'), [
            (Keyword, 'httpie'), (Keyword, 'post'),
            (Name, 'name'), (Operator, '='), (String, 'jack'),
            (Operator, '>'), (String, 'file.txt')
        ])

    def test_httpie_append_with_post_param(self):
        self.assertEqual(self.get_tokens('httpie post name=doe >> file.txt'), [
            (Keyword, 'httpie'), (Keyword, 'post'),
            (Name, 'name'), (Operator, '='), (String, 'doe'),
            (Operator, '>>'), (String, 'file.txt')
        ])

    def test_httpie_write_quoted_filename(self):
        self.assertEqual(self.get_tokens("httpie > 'my file.txt'"), [
            (Keyword, 'httpie'), (Operator, '>'),
            (Text, "'"), (String, 'my file.txt'), (Text, "'")
        ])

    def test_httpie_append_quoted_filename(self):
        self.assertEqual(self.get_tokens('httpie >> "my file.txt"'), [
            (Keyword, 'httpie'), (Operator, '>>'),
            (Text, '"'), (String, 'my file.txt'), (Text, '"')
        ])

    def test_httpie_append_with_many_params(self):
        command = ("httpie post --auth user:pass --verify=no  "
                   "name='john doe'  page==2 >> file.txt")
        self.assertEqual(self.get_tokens(command), [
            (Keyword, 'httpie'), (Keyword, 'post'),
            (Name, '--auth'), (String, 'user:pass'),
            (Name, '--verify'), (Operator, '='), (String, 'no'),
            (Name, 'name'), (Operator, '='),
            (Text, "'"), (String, 'john doe'), (Text, "'"),
            (Name, 'page'), (Operator, '=='), (String, '2'),
            (Operator, '>>'), (String, 'file.txt')
        ])

    def test_curl_write(self):
        self.assertEqual(self.get_tokens('curl > file.txt'), [
            (Keyword, 'curl'),
            (Operator, '>'), (String, 'file.txt')
        ])

    def test_curl_write_without_spaces(self):
        self.assertEqual(self.get_tokens('curl>file.txt'), [
            (Keyword, 'curl'),
            (Operator, '>'), (String, 'file.txt')
        ])

    def test_curl_append(self):
        self.assertEqual(self.get_tokens('curl >> file.txt'), [
            (Keyword, 'curl'),
            (Operator, '>>'), (String, 'file.txt')
        ])

    def test_curl_append_without_spaces(self):
        self.assertEqual(self.get_tokens('curl>>file.txt'), [
            (Keyword, 'curl'),
            (Operator, '>>'), (String, 'file.txt')
        ])

    def test_curl_write_with_post_param(self):
        self.assertEqual(self.get_tokens('curl post name=jack > file.txt'), [
            (Keyword, 'curl'), (Keyword, 'post'),
            (Name, 'name'), (Operator, '='), (String, 'jack'),
            (Operator, '>'), (String, 'file.txt')
        ])

    def test_curl_append_with_post_param(self):
        self.assertEqual(self.get_tokens('curl post name=doe >> file.txt'), [
            (Keyword, 'curl'), (Keyword, 'post'),
            (Name, 'name'), (Operator, '='), (String, 'doe'),
            (Operator, '>>'), (String, 'file.txt')
        ])

    def test_curl_write_quoted_filename(self):
        self.assertEqual(self.get_tokens("curl > 'my file.txt'"), [
            (Keyword, 'curl'), (Operator, '>'),
            (Text, "'"), (String, 'my file.txt'), (Text, "'")
        ])

    def test_curl_append_quoted_filename(self):
        self.assertEqual(self.get_tokens('curl >> "my file.txt"'), [
            (Keyword, 'curl'), (Operator, '>>'),
            (Text, '"'), (String, 'my file.txt'), (Text, '"')
        ])

    def test_curl_append_with_many_params(self):
        command = ("curl post --auth user:pass --verify=no  "
                   "name='john doe'  page==2 >> file.txt")
        self.assertEqual(self.get_tokens(command), [
            (Keyword, 'curl'), (Keyword, 'post'),
            (Name, '--auth'), (String, 'user:pass'),
            (Name, '--verify'), (Operator, '='), (String, 'no'),
            (Name, 'name'), (Operator, '='),
            (Text, "'"), (String, 'john doe'), (Text, "'"),
            (Name, 'page'), (Operator, '=='), (String, '2'),
            (Operator, '>>'), (String, 'file.txt')
        ])


class TestLexerAction(LexerTestCase):

    def test_get(self):
        self.assertEqual(self.get_tokens('get'), [
            (Keyword, 'get')
        ])

    def test_post_with_spaces(self):
        self.assertEqual(self.get_tokens('   post  '), [
            (Keyword, 'post')
        ])

    def test_capital_head(self):
        self.assertEqual(self.get_tokens('HEAD'), [
            (Keyword, 'HEAD')
        ])

    def test_delete_random_capitals(self):
        self.assertEqual(self.get_tokens('dElETe'), [
            (Keyword, 'dElETe')
        ])

    def test_patch(self):
        self.assertEqual(self.get_tokens('patch'), [
            (Keyword, 'patch')
        ])

    def test_get_with_querystring_params(self):
        command = 'get page==10 id==200'
        self.assertEqual(self.get_tokens(command), [
            (Keyword, 'get'),
            (Name, 'page'), (Operator, '=='), (String, '10'),
            (Name, 'id'), (Operator, '=='), (String, '200')
        ])

    def test_capital_get_with_querystring_params(self):
        command = 'GET page==10 id==200'
        self.assertEqual(self.get_tokens(command), [
            (Keyword, 'GET'),
            (Name, 'page'), (Operator, '=='), (String, '10'),
            (Name, 'id'), (Operator, '=='), (String, '200')
        ])

    def test_post_with_body_params(self):
        command = 'post name="john doe" username=john'
        self.assertEqual(self.get_tokens(command), [
            (Keyword, 'post'), (Name, 'name'), (Operator, '='),
            (Text, '"'), (String, 'john doe'), (Text, '"'),
            (Name, 'username'), (Operator, '='), (String, 'john')
        ])

    def test_post_with_spaces_and_body_params(self):
        command = '  post   name="john doe"     username=john  '
        self.assertEqual(self.get_tokens(command), [
            (Keyword, 'post'), (Name, 'name'), (Operator, '='),
            (Text, '"'), (String, 'john doe'), (Text, '"'),
            (Name, 'username'), (Operator, '='), (String, 'john')
        ])


class TestLexerActionRedirection(LexerTestCase):

    def test_get_write(self):
        self.assertEqual(self.get_tokens('get > file.txt'), [
            (Keyword, 'get'), (Operator, '>'), (String, 'file.txt')
        ])

    def test_get_write_quoted_filename(self):
        self.assertEqual(self.get_tokens('get > "/tmp/my file.txt"'), [
            (Keyword, 'get'), (Operator, '>'),
            (Text, '"'), (String, '/tmp/my file.txt'), (Text, '"')
        ])

    def test_get_append(self):
        self.assertEqual(self.get_tokens('get >> file.txt'), [
            (Keyword, 'get'), (Operator, '>>'), (String, 'file.txt')
        ])

    def test_get_append_escaped_filename(self):
        self.assertEqual(self.get_tokens(r'get >> /tmp/my\ file.txt'), [
            (Keyword, 'get'), (Operator, '>>'),
            (String, r'/tmp/my\ file.txt')
        ])

    def test_post_append_with_spaces(self):
        self.assertEqual(self.get_tokens('   post  >>   file.txt'), [
            (Keyword, 'post'), (Operator, '>>'), (String, 'file.txt')
        ])

    def test_capital_head_write(self):
        self.assertEqual(self.get_tokens('HEAD > file.txt'), [
            (Keyword, 'HEAD'), (Operator, '>'), (String, 'file.txt')
        ])

    def test_get_append_with_querystring_params(self):
        command = 'get page==10 id==200 >> /tmp/file.txt'
        self.assertEqual(self.get_tokens(command), [
            (Keyword, 'get'),
            (Name, 'page'), (Operator, '=='), (String, '10'),
            (Name, 'id'), (Operator, '=='), (String, '200'),
            (Operator, '>>'), (String, '/tmp/file.txt')
        ])

    def test_post_write_escaped_filename_with_body_params(self):
        command = r'post name="john doe" username=john > /tmp/my\ file.txt'
        self.assertEqual(self.get_tokens(command), [
            (Keyword, 'post'), (Name, 'name'), (Operator, '='),
            (Text, '"'), (String, 'john doe'), (Text, '"'),
            (Name, 'username'), (Operator, '='), (String, 'john'),
            (Operator, '>'), (String, r'/tmp/my\ file.txt')
        ])

    def test_post_append_with_spaces_and_body_params(self):
        command = ' post    name="john doe"  username=john  >> /tmp/file.txt  '
        self.assertEqual(self.get_tokens(command), [
            (Keyword, 'post'), (Name, 'name'), (Operator, '='),
            (Text, '"'), (String, 'john doe'), (Text, '"'),
            (Name, 'username'), (Operator, '='), (String, 'john'),
            (Operator, '>>'), (String, '/tmp/file.txt')
        ])
