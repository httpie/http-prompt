import unittest

from pygments.token import Keyword, String, Text, Error, Name

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


# TODO: Add more tests...
