# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import unittest

import pytest
import six

from mock import patch

from http_prompt.context import Context
from http_prompt.execution import execute


class ExecutionTestCase(unittest.TestCase):

    def setUp(self):
        self.patchers = [
            ('httpie_main', patch('http_prompt.execution.httpie_main')),
            ('click', patch('http_prompt.execution.click')),
        ]
        for attr_name, patcher in self.patchers:
            setattr(self, attr_name, patcher.start())

        self.context = Context('http://localhost')

    def tearDown(self):
        for _, patcher in self.patchers:
            patcher.stop()

    def assert_httpie_main_called_with(self, args):
        self.assertEqual(self.httpie_main.call_args[0][0], args)


class TestExecution_noop(ExecutionTestCase):

    def test_empty_string(self):
        execute('', self.context)
        self.assertEqual(self.context.url, 'http://localhost')
        self.assertFalse(self.context.options)
        self.assertFalse(self.context.headers)
        self.assertFalse(self.context.querystring_params)
        self.assertFalse(self.context.body_params)
        self.assertFalse(self.context.should_exit)

    def test_spaces(self):
        execute('  \t \t  ', self.context)
        self.assertEqual(self.context.url, 'http://localhost')
        self.assertFalse(self.context.options)
        self.assertFalse(self.context.headers)
        self.assertFalse(self.context.querystring_params)
        self.assertFalse(self.context.body_params)
        self.assertFalse(self.context.should_exit)


class TestExecution_help(ExecutionTestCase):

    def test_help(self):
        execute('help', self.context)
        help_text = self.click.echo_via_pager.call_args[0][0]
        self.assertTrue(help_text.startswith('Commands:\n\tcd'))

    def test_help_with_spaces(self):
        execute('  help   ', self.context)
        help_text = self.click.echo_via_pager.call_args[0][0]
        self.assertTrue(help_text.startswith('Commands:\n\tcd'))


class TestExecution_exit(ExecutionTestCase):

    def test_exit(self):
        execute('exit', self.context)
        self.assertTrue(self.context.should_exit)

    def test_exit_with_spaces(self):
        execute('   exit  ', self.context)
        self.assertTrue(self.context.should_exit)


class TestExecution_cd(ExecutionTestCase):

    def test_single_level(self):
        execute('cd api', self.context)
        self.assertEqual(self.context.url, 'http://localhost/api')

    def test_many_levels(self):
        execute('cd api/v2/movie/50', self.context)
        self.assertEqual(self.context.url, 'http://localhost/api/v2/movie/50')

    def test_change_base(self):
        execute('cd //example.com/api', self.context)
        self.assertEqual(self.context.url, 'http://example.com/api')

    def test_root(self):
        execute('cd /api/v2', self.context)
        self.assertEqual(self.context.url, 'http://localhost/api/v2')

        execute('cd /index.html', self.context)
        self.assertEqual(self.context.url, 'http://localhost/index.html')

    def test_dot_dot(self):
        execute('cd api/v1', self.context)
        self.assertEqual(self.context.url, 'http://localhost/api/v1')

        execute('cd ..', self.context)
        self.assertEqual(self.context.url, 'http://localhost/api')

        # If dot-dot has a trailing slash, the resulting URL should have a
        # trailing slash
        execute('cd ../rest/api/', self.context)
        self.assertEqual(self.context.url, 'http://localhost/rest/api/')

    def test_url_with_trailing_slash(self):
        self.context.url = 'http://localhost/'
        execute('cd api', self.context)
        self.assertEqual(self.context.url, 'http://localhost/api')

        execute('cd v2/', self.context)
        self.assertEqual(self.context.url, 'http://localhost/api/v2/')

        execute('cd /objects/', self.context)
        self.assertEqual(self.context.url, 'http://localhost/objects/')

    def test_path_with_trailing_slash(self):
        execute('cd api/', self.context)
        self.assertEqual(self.context.url, 'http://localhost/api/')

        execute('cd movie/1/', self.context)
        self.assertEqual(self.context.url, 'http://localhost/api/movie/1/')


class TestExecution_rm(ExecutionTestCase):

    def test_header(self):
        self.context.headers['Content-Type'] = 'text/html'
        execute('rm -h Content-Type', self.context)
        self.assertFalse(self.context.headers)

    def test_option(self):
        self.context.options['--form'] = None
        execute('rm -o --form', self.context)
        self.assertFalse(self.context.options)

    def test_querystring(self):
        self.context.querystring_params['page'] = '1'
        execute('rm -q page', self.context)
        self.assertFalse(self.context.querystring_params)

    def test_body_param(self):
        self.context.body_params['name'] = 'alice'
        execute('rm -b name', self.context)
        self.assertFalse(self.context.body_params)

    def test_header_single_quoted(self):
        self.context.headers['Content-Type'] = 'text/html'
        execute("rm -h 'Content-Type'", self.context)
        self.assertFalse(self.context.headers)

    def test_option_double_quoted(self):
        self.context.options['--form'] = None
        execute('rm -o "--form"', self.context)
        self.assertFalse(self.context.options)

    def test_querystring_double_quoted(self):
        self.context.querystring_params['page size'] = '10'
        execute('rm -q "page size"', self.context)
        self.assertFalse(self.context.querystring_params)

    def test_body_param_double_quoted(self):
        self.context.body_params['family name'] = 'Doe Doe'
        execute('rm -b "family name"', self.context)
        self.assertFalse(self.context.body_params)

    def test_body_param_escaped(self):
        self.context.body_params['family name'] = 'Doe Doe'
        execute('rm -b family\ name', self.context)
        self.assertFalse(self.context.body_params)

    def test_non_existing_key(self):
        execute('rm -q abcd', self.context)
        err_msg = self.click.secho.call_args[0][0]
        self.assertEqual(err_msg, "Key 'abcd' not found")

    @pytest.mark.skipif(not six.PY2, reason='a bug on Python 2')
    def test_non_existing_key_unicode(self):  # See #25
        execute(u'rm -q abcd', self.context)
        err_msg = self.click.secho.call_args[0][0]
        self.assertEqual(err_msg, "Key 'abcd' not found")

    def test_reset(self):
        self.context.options.update({
            '--form': None,
            '--verify': 'no'
        })
        self.context.headers.update({
            'Accept': 'dontcare',
            'Content-Type': 'dontcare'
        })
        self.context.querystring_params.update({
            'name': 'dontcare',
            'email': 'dontcare'
        })
        self.context.body_params.update({
            'name': 'dontcare',
            'email': 'dontcare'
        })

        execute('rm *', self.context)

        self.assertFalse(self.context.options)
        self.assertFalse(self.context.headers)
        self.assertFalse(self.context.querystring_params)
        self.assertFalse(self.context.body_params)


class TestMutation(ExecutionTestCase):

    def test_simple_headers(self):
        execute('Accept:text/html User-Agent:HttpPrompt', self.context)
        self.assertEqual(self.context.headers, {
            'Accept': 'text/html',
            'User-Agent': 'HttpPrompt'
        })

    def test_header_value_with_double_quotes(self):
        execute('Accept:text/html User-Agent:"HTTP Prompt"', self.context)
        self.assertEqual(self.context.headers, {
            'Accept': 'text/html',
            'User-Agent': 'HTTP Prompt'
        })

    def test_header_value_with_single_quotes(self):
        execute("Accept:text/html User-Agent:'HTTP Prompt'", self.context)
        self.assertEqual(self.context.headers, {
            'Accept': 'text/html',
            'User-Agent': 'HTTP Prompt'
        })

    def test_header_with_double_quotes(self):
        execute('Accept:text/html "User-Agent:HTTP Prompt"', self.context)
        self.assertEqual(self.context.headers, {
            'Accept': 'text/html',
            'User-Agent': 'HTTP Prompt'
        })

    def test_header_with_single_quotes(self):
        execute("Accept:text/html 'User-Agent:HTTP Prompt'", self.context)
        self.assertEqual(self.context.headers, {
            'Accept': 'text/html',
            'User-Agent': 'HTTP Prompt'
        })

    def test_header_escaped_chars(self):
        execute(r'X-Name:John\'s\ Doe', self.context)
        self.assertEqual(self.context.headers, {
            'X-Name': "John's Doe"
        })

    def test_header_value_escaped_quote(self):
        execute(r"'X-Name:John\'s Doe'", self.context)
        self.assertEqual(self.context.headers, {
            'X-Name': "John's Doe"
        })

    def test_simple_querystring(self):
        execute('page==1 limit==20', self.context)
        self.assertEqual(self.context.querystring_params, {
            'page': ['1'],
            'limit': ['20']
        })

    def test_querystring_with_double_quotes(self):
        execute('page==1 name=="John Doe"', self.context)
        self.assertEqual(self.context.querystring_params, {
            'page': ['1'],
            'name': ['John Doe']
        })

    def test_querystring_with_single_quotes(self):
        execute("page==1 name=='John Doe'", self.context)
        self.assertEqual(self.context.querystring_params, {
            'page': ['1'],
            'name': ['John Doe']
        })

    def test_querystring_with_chinese(self):
        execute("name==王小明", self.context)
        self.assertEqual(self.context.querystring_params, {
            'name': ['王小明']
        })

    def test_querystring_escaped_chars(self):
        execute(r'name==John\'s\ Doe', self.context)
        self.assertEqual(self.context.querystring_params, {
            'name': ["John's Doe"]
        })

    def test_querytstring_value_escaped_quote(self):
        execute(r"'name==John\'s Doe'", self.context)
        self.assertEqual(self.context.querystring_params, {
            'name': ["John's Doe"]
        })

    def test_querystring_key_escaped_quote(self):
        execute(r"'john\'s last name==Doe'", self.context)
        self.assertEqual(self.context.querystring_params, {
            "john's last name": ['Doe']
        })

    def test_simple_body_params(self):
        execute('username=john password=123', self.context)
        self.assertEqual(self.context.body_params, {
            'username': 'john',
            'password': '123'
        })

    def test_body_param_value_with_double_quotes(self):
        execute('name="John Doe" password=123', self.context)
        self.assertEqual(self.context.body_params, {
            'name': 'John Doe',
            'password': '123'
        })

    def test_body_param_value_with_single_quotes(self):
        execute("name='John Doe' password=123", self.context)
        self.assertEqual(self.context.body_params, {
            'name': 'John Doe',
            'password': '123'
        })

    def test_body_param_with_double_quotes(self):
        execute('"name=John Doe" password=123', self.context)
        self.assertEqual(self.context.body_params, {
            'name': 'John Doe',
            'password': '123'
        })

    def test_body_param_with_spanish(self):
        execute('name=Jesús', self.context)
        self.assertEqual(self.context.body_params, {
            'name': 'Jesús'
        })

    def test_body_param_escaped_chars(self):
        execute(r'name=John\'s\ Doe', self.context)
        self.assertEqual(self.context.body_params, {
            'name': "John's Doe"
        })

    def test_body_param_value_escaped_quote(self):
        execute(r"'name=John\'s Doe'", self.context)
        self.assertEqual(self.context.body_params, {
            'name': "John's Doe"
        })

    def test_body_param_key_escaped_quote(self):
        execute(r"'john\'s last name=Doe'", self.context)
        self.assertEqual(self.context.body_params, {
            "john's last name": 'Doe'
        })

    def test_long_option_names(self):
        execute('--auth user:pass --form', self.context)
        self.assertEqual(self.context.options, {
            '--form': None,
            '--auth': 'user:pass'
        })

    def test_long_option_names_with_its_prefix(self):
        execute('--auth-type basic --auth user:pass --session user '
                '--session-read-only user', self.context)
        self.assertEqual(self.context.options, {
            '--auth-type': 'basic',
            '--auth': 'user:pass',
            '--session-read-only': 'user',
            '--session': 'user'
        })

    def test_long_short_option_names_mixed(self):
        execute('--style=default -j --stream', self.context)
        self.assertEqual(self.context.options, {
            '-j': None,
            '--stream': None,
            '--style': 'default'
        })

    def test_option_and_body_param(self):
        execute('--form name="John Doe"', self.context)
        self.assertEqual(self.context.options, {
            '--form': None
        })
        self.assertEqual(self.context.body_params, {
            'name': 'John Doe'
        })

    def test_mixed(self):
        execute('   --form  name="John Doe"   password=1234\ 5678    '
                'User-Agent:HTTP\ Prompt  -a   \'john:1234 5678\'  '
                '"Accept:text/html"  ', self.context)
        self.assertEqual(self.context.options, {
            '--form': None,
            '-a': 'john:1234 5678'
        })
        self.assertEqual(self.context.headers, {
            'User-Agent': 'HTTP Prompt',
            'Accept': 'text/html'
        })
        self.assertEqual(self.context.options, {
            '--form': None,
            '-a': 'john:1234 5678'
        })
        self.assertEqual(self.context.body_params, {
            'name': 'John Doe',
            'password': '1234 5678'
        })

    def test_multi_querystring(self):
        execute('name==john name==doe', self.context)
        self.assertEqual(self.context.querystring_params, {
            'name': ['john', 'doe']
        })

        execute('name==jane', self.context)
        self.assertEqual(self.context.querystring_params, {
            'name': ['jane']
        })


class TestHttpAction(ExecutionTestCase):

    def test_get(self):
        execute('get', self.context)
        self.assert_httpie_main_called_with(['GET', 'http://localhost'])

    def test_get_uppercase(self):
        execute('GET', self.context)
        self.assert_httpie_main_called_with(['GET', 'http://localhost'])

    def test_get_multi_querystring(self):
        execute('get foo==1 foo==2 foo==3', self.context)
        self.assert_httpie_main_called_with([
            'GET', 'http://localhost', 'foo==1', 'foo==2', 'foo==3'])

    def test_post(self):
        execute('post page==1', self.context)
        self.assert_httpie_main_called_with(['POST', 'http://localhost',
                                             'page==1'])
        self.assertFalse(self.context.querystring_params)

    def test_post_with_absolute_path(self):
        execute('post /api/v3 name=bob', self.context)
        self.assert_httpie_main_called_with(['POST', 'http://localhost/api/v3',
                                             'name=bob'])
        self.assertFalse(self.context.body_params)
        self.assertEqual(self.context.url, 'http://localhost')

    def test_post_with_relative_path(self):
        self.context.url = 'http://localhost/api/v3'
        execute('post ../v2/movie id=8', self.context)
        self.assert_httpie_main_called_with([
            'POST', 'http://localhost/api/v2/movie', 'id=8'])
        self.assertFalse(self.context.body_params)
        self.assertEqual(self.context.url, 'http://localhost/api/v3')

    def test_post_with_full_url(self):
        execute('post http://httpbin.org/post id=9', self.context)
        self.assert_httpie_main_called_with([
            'POST', 'http://httpbin.org/post', 'id=9'])
        self.assertFalse(self.context.body_params)
        self.assertEqual(self.context.url, 'http://localhost')

    def test_post_with_full_https_url(self):
        execute('post https://httpbin.org/post id=9', self.context)
        self.assert_httpie_main_called_with([
            'POST', 'https://httpbin.org/post', 'id=9'])
        self.assertFalse(self.context.body_params)
        self.assertEqual(self.context.url, 'http://localhost')

    def test_post_uppercase(self):
        execute('POST content=text', self.context)
        self.assert_httpie_main_called_with(['POST', 'http://localhost',
                                             'content=text'])
        self.assertFalse(self.context.body_params)

    def test_delete(self):
        execute('delete', self.context)
        self.assert_httpie_main_called_with(['DELETE', 'http://localhost'])

    def test_delete_uppercase(self):
        execute('DELETE', self.context)
        self.assert_httpie_main_called_with(['DELETE', 'http://localhost'])

    def test_patch(self):
        execute('patch', self.context)
        self.assert_httpie_main_called_with(['PATCH', 'http://localhost'])

    def test_patch_uppercase(self):
        execute('PATCH', self.context)
        self.assert_httpie_main_called_with(['PATCH', 'http://localhost'])

    def test_head(self):
        execute('head', self.context)
        self.assert_httpie_main_called_with(['HEAD', 'http://localhost'])

    def test_head_uppercase(self):
        execute('HEAD', self.context)
        self.assert_httpie_main_called_with(['HEAD', 'http://localhost'])


class TestCommandPreview(ExecutionTestCase):

    def test_httpie_without_args(self):
        execute('httpie', self.context)
        self.click.echo.assert_called_with('http http://localhost')

    def test_httpie_with_post(self):
        execute('httpie post name=alice', self.context)
        self.click.echo.assert_called_with(
            'http POST http://localhost name=alice')
        self.assertFalse(self.context.body_params)

    def test_httpie_with_absolute_path(self):
        execute('httpie post /api name=alice', self.context)
        self.click.echo.assert_called_with(
            'http POST http://localhost/api name=alice')
        self.assertFalse(self.context.body_params)

    def test_httpie_with_full_url(self):
        execute('httpie post http://httpbin.org/post name=alice', self.context)
        self.click.echo.assert_called_with(
            'http POST http://httpbin.org/post name=alice')
        self.assertEqual(self.context.url, 'http://localhost')
        self.assertFalse(self.context.body_params)

    def test_httpie_with_full_https_url(self):
        execute('httpie post https://httpbin.org/post name=alice',
                self.context)
        self.click.echo.assert_called_with(
            'http POST https://httpbin.org/post name=alice')
        self.assertEqual(self.context.url, 'http://localhost')
        self.assertFalse(self.context.body_params)

    def test_httpie_with_quotes(self):
        execute(r'httpie post http://httpbin.org/post name="john doe" '
                r"apikey==abc\ 123 'Authorization:ApiKey 1234'",
                self.context)
        self.click.echo.assert_called_with(
            "http POST http://httpbin.org/post 'apikey==abc 123' "
            "'name=john doe' 'Authorization:ApiKey 1234'")
        self.assertEqual(self.context.url, 'http://localhost')
        self.assertFalse(self.context.body_params)
        self.assertFalse(self.context.querystring_params)
        self.assertFalse(self.context.headers)

    def test_httpie_with_multi_querystring(self):
        execute('httpie get foo==1 foo==2 foo==3', self.context)
        self.click.echo.assert_called_with(
            'http GET http://localhost foo==1 foo==2 foo==3')
        self.assertEqual(self.context.url, 'http://localhost')
        self.assertFalse(self.context.querystring_params)
