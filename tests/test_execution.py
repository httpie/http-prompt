# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import hashlib
import io
import json
import shutil
import sys

import pytest
import six

from mock import patch

from http_prompt.context import Context
from http_prompt.execution import execute

from .base import TempAppDirTestCase


class ExecutionTestCase(TempAppDirTestCase):

    def setUp(self):
        super(ExecutionTestCase, self).setUp()
        self.patchers = [
            ('httpie_main', patch('http_prompt.execution.httpie_main')),
            ('echo_via_pager',
             patch('http_prompt.output.click.echo_via_pager')),
            ('secho', patch('http_prompt.execution.click.secho'))
        ]
        for attr_name, patcher in self.patchers:
            setattr(self, attr_name, patcher.start())

        self.context = Context('http://localhost')

    def tearDown(self):
        super(ExecutionTestCase, self).tearDown()
        for _, patcher in self.patchers:
            patcher.stop()

    def assert_httpie_main_called_with(self, args):
        self.assertEqual(self.httpie_main.call_args[0][0], args)

    def assert_stdout(self, expected_msg):
        printed_msg = self.echo_via_pager.call_args[0][0]
        self.assertEqual(printed_msg, expected_msg)

    def assert_stderr(self, expected_msg):
        printed_msg = self.secho.call_args[0][0]
        print_options = self.secho.call_args[1]
        self.assertEqual(printed_msg, expected_msg)
        self.assertEqual(print_options, {'err': True, 'fg': 'red'})


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


class TestExecution_env(ExecutionTestCase):

    def setUp(self):
        super(TestExecution_env, self).setUp()

        self.context.url = 'http://localhost:8000/api'
        self.context.headers.update({
            'Accept': 'text/csv',
            'Authorization': 'ApiKey 1234'
        })
        self.context.querystring_params.update({
            'page': ['1'],
            'limit': ['50']
        })
        self.context.body_params.update({
            'name': 'John Doe'
        })
        self.context.options.update({
            '--verify': 'no',
            '--form': None
        })

    def test_env(self):
        execute('env', self.context)
        self.assert_stdout("--form\n--verify=no\n"
                           "cd http://localhost:8000/api\n"
                           "limit==50\npage==1\n"
                           "'name=John Doe'\n"
                           "Accept:text/csv\n"
                           "'Authorization:ApiKey 1234'\n")

    def test_env_with_spaces(self):
        execute('  env   ', self.context)
        self.assert_stdout("--form\n--verify=no\n"
                           "cd http://localhost:8000/api\n"
                           "limit==50\npage==1\n"
                           "'name=John Doe'\n"
                           "Accept:text/csv\n"
                           "'Authorization:ApiKey 1234'\n")

    def test_env_non_ascii(self):
        self.context.body_params['name'] = '許 功蓋'
        execute('env', self.context)
        self.assert_stdout("--form\n--verify=no\n"
                           "cd http://localhost:8000/api\n"
                           "limit==50\npage==1\n"
                           "'name=許 功蓋'\n"
                           "Accept:text/csv\n"
                           "'Authorization:ApiKey 1234'\n")

    def test_env_write_to_file(self):
        filename = self.make_tempfile()

        # write something first to make sure it's a full overwrite
        with open(filename, 'w') as f:
            f.write('hello world\n')

        execute('env > %s' % filename, self.context)

        with open(filename) as f:
            content = f.read()

        self.assertEqual(content,
                         "--form\n--verify=no\n"
                         "cd http://localhost:8000/api\n"
                         "limit==50\npage==1\n"
                         "'name=John Doe'\n"
                         "Accept:text/csv\n"
                         "'Authorization:ApiKey 1234'\n")

    def test_env_non_ascii_and_write_to_file(self):
        filename = self.make_tempfile()

        # write something first to make sure it's a full overwrite
        with open(filename, 'w') as f:
            f.write('hello world\n')

        self.context.body_params['name'] = '許 功蓋'
        execute('env > %s' % filename, self.context)

        with io.open(filename, encoding='utf-8') as f:
            content = f.read()

        self.assertEqual(content,
                         "--form\n--verify=no\n"
                         "cd http://localhost:8000/api\n"
                         "limit==50\npage==1\n"
                         "'name=許 功蓋'\n"
                         "Accept:text/csv\n"
                         "'Authorization:ApiKey 1234'\n")

    def test_env_write_to_quoted_filename(self):
        filename = self.make_tempfile()

        # Write something first to make sure it's a full overwrite
        with open(filename, 'w') as f:
            f.write('hello world\n')

        execute("env > '%s'" % filename, self.context)

        with open(filename) as f:
            content = f.read()

        self.assertEqual(content,
                         "--form\n--verify=no\n"
                         "cd http://localhost:8000/api\n"
                         "limit==50\npage==1\n"
                         "'name=John Doe'\n"
                         "Accept:text/csv\n"
                         "'Authorization:ApiKey 1234'\n")

    def test_env_append_to_file(self):
        filename = self.make_tempfile()

        # Write something first to make sure it's an append
        with open(filename, 'w') as f:
            f.write('hello world\n')

        execute('env >> %s' % filename, self.context)

        with open(filename) as f:
            content = f.read()

        self.assertEqual(content,
                         "hello world\n"
                         "--form\n--verify=no\n"
                         "cd http://localhost:8000/api\n"
                         "limit==50\npage==1\n"
                         "'name=John Doe'\n"
                         "Accept:text/csv\n"
                         "'Authorization:ApiKey 1234'\n")


class TestExecution_source_and_exec(ExecutionTestCase):

    def setUp(self):
        super(TestExecution_source_and_exec, self).setUp()

        self.context.url = 'http://localhost:8000/api'
        self.context.headers.update({
            'Accept': 'text/csv',
            'Authorization': 'ApiKey 1234'
        })
        self.context.querystring_params.update({
            'page': ['1'],
            'limit': ['50']
        })
        self.context.body_params.update({
            'name': 'John Doe'
        })
        self.context.options.update({
            '--verify': 'no',
            '--form': None
        })

        # The file that is about to be sourced/exec'd
        self.filename = self.make_tempfile(
            "Language:en Authorization:'ApiKey 5678'\n"
            "name='Jane Doe'  username=jane   limit==25\n"
            "rm -o --form\n"
            "cd v2/user\n")

    def test_source(self):
        execute('source %s' % self.filename, self.context)

        self.assertEqual(self.context.url,
                         'http://localhost:8000/api/v2/user')
        self.assertEqual(self.context.headers, {
            'Accept': 'text/csv',
            'Authorization': 'ApiKey 5678',
            'Language': 'en'
        })
        self.assertEqual(self.context.querystring_params, {
            'page': ['1'],
            'limit': ['25']
        })
        self.assertEqual(self.context.body_params, {
            'name': 'Jane Doe',
            'username': 'jane'
        })
        self.assertEqual(self.context.options, {
            '--verify': 'no'
        })

    def test_source_with_spaces(self):
        execute(' source       %s   ' % self.filename, self.context)

        self.assertEqual(self.context.url,
                         'http://localhost:8000/api/v2/user')
        self.assertEqual(self.context.headers, {
            'Accept': 'text/csv',
            'Authorization': 'ApiKey 5678',
            'Language': 'en'
        })
        self.assertEqual(self.context.querystring_params, {
            'page': ['1'],
            'limit': ['25']
        })
        self.assertEqual(self.context.body_params, {
            'name': 'Jane Doe',
            'username': 'jane'
        })
        self.assertEqual(self.context.options, {
            '--verify': 'no'
        })

    def test_source_non_existing_file(self):
        c = self.context.copy()
        execute('source no_such_file.txt', self.context)
        self.assertEqual(self.context, c)

        # Try to get the error message when opening a non-existing file
        try:
            with open('no_such_file.txt'):
                pass
        except IOError as err:
            # The 'replace' part is to fix an issue where Python 2 converts
            # the unicode filename to "u'FILENAME'"
            err_msg = str(err).replace("u'", "'")
        else:
            assert False, 'what?! no_such_file.txt exists!'

        self.assert_stderr(err_msg)

    def test_source_quoted_filename(self):
        execute('source "%s"' % self.filename, self.context)

        self.assertEqual(self.context.url,
                         'http://localhost:8000/api/v2/user')
        self.assertEqual(self.context.headers, {
            'Accept': 'text/csv',
            'Authorization': 'ApiKey 5678',
            'Language': 'en'
        })
        self.assertEqual(self.context.querystring_params, {
            'page': ['1'],
            'limit': ['25']
        })
        self.assertEqual(self.context.body_params, {
            'name': 'Jane Doe',
            'username': 'jane'
        })
        self.assertEqual(self.context.options, {
            '--verify': 'no'
        })

    def test_source_escaped_filename(self):
        new_filename = self.filename + r' copy'
        shutil.copyfile(self.filename, new_filename)

        new_filename = new_filename.replace(' ', r'\ ')

        execute('source %s' % new_filename, self.context)

        self.assertEqual(self.context.url,
                         'http://localhost:8000/api/v2/user')
        self.assertEqual(self.context.headers, {
            'Accept': 'text/csv',
            'Authorization': 'ApiKey 5678',
            'Language': 'en'
        })
        self.assertEqual(self.context.querystring_params, {
            'page': ['1'],
            'limit': ['25']
        })
        self.assertEqual(self.context.body_params, {
            'name': 'Jane Doe',
            'username': 'jane'
        })
        self.assertEqual(self.context.options, {
            '--verify': 'no'
        })

    def test_exec(self):
        execute('exec %s' % self.filename, self.context)

        self.assertEqual(self.context.url,
                         'http://localhost:8000/api/v2/user')
        self.assertEqual(self.context.headers, {
            'Authorization': 'ApiKey 5678',
            'Language': 'en'
        })
        self.assertEqual(self.context.querystring_params, {
            'limit': ['25']
        })
        self.assertEqual(self.context.body_params, {
            'name': 'Jane Doe',
            'username': 'jane'
        })

    def test_exec_with_spaces(self):
        execute('  exec    %s   ' % self.filename, self.context)

        self.assertEqual(self.context.url,
                         'http://localhost:8000/api/v2/user')
        self.assertEqual(self.context.headers, {
            'Authorization': 'ApiKey 5678',
            'Language': 'en'
        })
        self.assertEqual(self.context.querystring_params, {
            'limit': ['25']
        })
        self.assertEqual(self.context.body_params, {
            'name': 'Jane Doe',
            'username': 'jane'
        })

    def test_exec_non_existing_file(self):
        c = self.context.copy()
        execute('exec no_such_file.txt', self.context)
        self.assertEqual(self.context, c)

        # Try to get the error message when opening a non-existing file
        try:
            with open('no_such_file.txt'):
                pass
        except IOError as err:
            # The 'replace' part is to fix an issue where Python 2 converts
            # the unicode filename to "u'FILENAME'"
            err_msg = str(err).replace("u'", "'")
        else:
            assert False, 'what?! no_such_file.txt exists!'

        self.assert_stderr(err_msg)

    def test_exec_quoted_filename(self):
        execute("exec '%s'" % self.filename, self.context)

        self.assertEqual(self.context.url,
                         'http://localhost:8000/api/v2/user')
        self.assertEqual(self.context.headers, {
            'Authorization': 'ApiKey 5678',
            'Language': 'en'
        })
        self.assertEqual(self.context.querystring_params, {
            'limit': ['25']
        })
        self.assertEqual(self.context.body_params, {
            'name': 'Jane Doe',
            'username': 'jane'
        })

    def test_exec_escaped_filename(self):
        new_filename = self.filename + r' copy'
        shutil.copyfile(self.filename, new_filename)

        new_filename = new_filename.replace(' ', r'\ ')

        execute('exec %s' % new_filename, self.context)
        self.assertEqual(self.context.url,
                         'http://localhost:8000/api/v2/user')
        self.assertEqual(self.context.headers, {
            'Authorization': 'ApiKey 5678',
            'Language': 'en'
        })
        self.assertEqual(self.context.querystring_params, {
            'limit': ['25']
        })
        self.assertEqual(self.context.body_params, {
            'name': 'Jane Doe',
            'username': 'jane'
        })


class TestExecution_env_and_source(ExecutionTestCase):

    def test_env_and_source(self):
        c = Context()
        c.url = 'http://localhost:8000/api'
        c.headers.update({
            'Accept': 'text/csv',
            'Authorization': 'ApiKey 1234'
        })
        c.querystring_params.update({
            'page': ['1'],
            'limit': ['50']
        })
        c.body_params.update({
            'name': 'John Doe'
        })
        c.options.update({
            '--verify': 'no',
            '--form': None
        })

        c2 = c.copy()

        filename = self.make_tempfile()
        execute('env > %s' % filename, c)
        execute('rm *', c)

        self.assertFalse(c.headers)
        self.assertFalse(c.querystring_params)
        self.assertFalse(c.body_params)
        self.assertFalse(c.options)

        execute('source %s' % filename, c)

        self.assertEqual(c, c2)

    def test_env_and_source_non_ascii(self):
        c = Context()
        c.url = 'http://localhost:8000/api'
        c.headers.update({
            'Accept': 'text/csv',
            'Authorization': 'ApiKey 1234'
        })
        c.querystring_params.update({
            'page': ['1'],
            'limit': ['50']
        })
        c.body_params.update({
            'name': '許 功蓋'
        })
        c.options.update({
            '--verify': 'no',
            '--form': None
        })

        c2 = c.copy()

        filename = self.make_tempfile()
        execute('env > %s' % filename, c)
        execute('rm *', c)

        self.assertFalse(c.headers)
        self.assertFalse(c.querystring_params)
        self.assertFalse(c.body_params)
        self.assertFalse(c.options)

        execute('source %s' % filename, c)

        self.assertEqual(c, c2)


class TestExecution_help(ExecutionTestCase):

    def test_help(self):
        execute('help', self.context)
        help_text = self.echo_via_pager.call_args[0][0]
        self.assertTrue(help_text.startswith('Commands:\n\tcd'))

    def test_help_with_spaces(self):
        execute('  help   ', self.context)
        help_text = self.echo_via_pager.call_args[0][0]
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
        self.assert_stderr("Key 'abcd' not found")

    @pytest.mark.skipif(not six.PY2, reason='a bug on Python 2')
    def test_non_existing_key_unicode(self):  # See #25
        execute(u'rm -q abcd', self.context)
        self.assert_stderr("Key 'abcd' not found")

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


class TestHttpActionRedirection(ExecutionTestCase):

    def test_get(self):
        execute('get > data.json', self.context)
        self.assert_httpie_main_called_with(['GET', 'http://localhost'])

        env = self.httpie_main.call_args[1]['env']
        self.assertFalse(env.stdout_isatty)
        self.assertEqual(env.stdout.fp.name, 'data.json')


@pytest.mark.slow
class TestHttpBin(TempAppDirTestCase):
    """Send real requests to http://httpbin.org, save the responses to files,
    and asserts on the file content.
    """
    def setUp(self):
        super(TestHttpBin, self).setUp()

        # XXX: pytest doesn't allow HTTPie to read stdin while it's capturing
        # stdout, so we replace stdin with a file temporarily during the test.
        self.orig_stdin = sys.stdin
        filename = self.make_tempfile()
        sys.stdin = open(filename, 'rb')
        sys.stdin.isatty = lambda: True

    def tearDown(self):
        sys.stdin.close()
        sys.stdin = self.orig_stdin

        super(TestHttpBin, self).tearDown()

    def execute(self, command):
        context = Context('http://httpbin.org')
        filename = self.make_tempfile()
        execute('%s > %s' % (command, filename), context)

        with open(filename, 'rb') as f:
            return f.read()

    def test_get_image(self):
        data = self.execute('get /image/png')
        self.assertTrue(data)
        self.assertEqual(hashlib.sha1(data).hexdigest(),
                         '379f5137831350c900e757b39e525b9db1426d53')

    def test_get_querystring(self):
        data = self.execute('get /get id==1234 X-Custom-Header:5678')
        data = json.loads(data.decode('utf-8'))
        self.assertEqual(data['args'], {
            'id': '1234'
        })
        self.assertEqual(data['headers']['X-Custom-Header'], '5678')

    def test_post_json(self):
        data = self.execute('post /post id=1234 X-Custom-Header:5678')
        data = json.loads(data.decode('utf-8'))
        self.assertEqual(data['json'], {
            'id': '1234'
        })
        self.assertEqual(data['headers']['X-Custom-Header'], '5678')

    def test_post_form(self):
        data = self.execute('post /post --form id=1234 X-Custom-Header:5678')
        data = json.loads(data.decode('utf-8'))
        print(data)
        self.assertEqual(data['form'], {
            'id': '1234'
        })
        self.assertEqual(data['headers']['X-Custom-Header'], '5678')


class TestCommandPreview(ExecutionTestCase):

    def test_httpie_without_args(self):
        execute('httpie', self.context)
        self.assert_stdout('http http://localhost')

    def test_httpie_with_post(self):
        execute('httpie post name=alice', self.context)
        self.assert_stdout('http POST http://localhost name=alice')
        self.assertFalse(self.context.body_params)

    def test_httpie_with_absolute_path(self):
        execute('httpie post /api name=alice', self.context)
        self.assert_stdout('http POST http://localhost/api name=alice')
        self.assertFalse(self.context.body_params)

    def test_httpie_with_full_url(self):
        execute('httpie POST http://httpbin.org/post name=alice', self.context)
        self.assert_stdout('http POST http://httpbin.org/post name=alice')
        self.assertEqual(self.context.url, 'http://localhost')
        self.assertFalse(self.context.body_params)

    def test_httpie_with_full_https_url(self):
        execute('httpie post https://httpbin.org/post name=alice',
                self.context)
        self.assert_stdout('http POST https://httpbin.org/post name=alice')
        self.assertEqual(self.context.url, 'http://localhost')
        self.assertFalse(self.context.body_params)

    def test_httpie_with_quotes(self):
        execute(r'httpie post http://httpbin.org/post name="john doe" '
                r"apikey==abc\ 123 'Authorization:ApiKey 1234'",
                self.context)
        self.assert_stdout(
            "http POST http://httpbin.org/post 'apikey==abc 123' "
            "'name=john doe' 'Authorization:ApiKey 1234'")
        self.assertEqual(self.context.url, 'http://localhost')
        self.assertFalse(self.context.body_params)
        self.assertFalse(self.context.querystring_params)
        self.assertFalse(self.context.headers)

    def test_httpie_with_multi_querystring(self):
        execute('httpie get foo==1 foo==2 foo==3', self.context)
        self.assert_stdout('http GET http://localhost foo==1 foo==2 foo==3')
        self.assertEqual(self.context.url, 'http://localhost')
        self.assertFalse(self.context.querystring_params)


class TestCommandPreviewRedirection(ExecutionTestCase):

    def test_httpie_redirect_write(self):
        filename = self.make_tempfile()

        # Write something first to make sure it's a full overwrite
        with open(filename, 'w') as f:
            f.write('hello world\n')

        execute('httpie > %s' % filename, self.context)

        with open(filename) as f:
            content = f.read()
        self.assertEqual(content, 'http http://localhost')

    def test_httpie_redirect_write_quoted_filename(self):
        filename = self.make_tempfile()

        # Write something first to make sure it's a full overwrite
        with open(filename, 'w') as f:
            f.write('hello world\n')

        execute('httpie > "%s"' % filename, self.context)

        with open(filename) as f:
            content = f.read()
        self.assertEqual(content, 'http http://localhost')

    def test_httpie_redirect_write_with_args(self):
        filename = self.make_tempfile()

        # Write something first to make sure it's a full overwrite
        with open(filename, 'w') as f:
            f.write('hello world\n')

        execute('httpie post http://example.org name=john > %s' % filename,
                self.context)

        with open(filename) as f:
            content = f.read()
        self.assertEqual(content, 'http POST http://example.org name=john')

    def test_httpie_redirect_append(self):
        filename = self.make_tempfile()

        # Write something first to make sure it's an append
        with open(filename, 'w') as f:
            f.write('hello world\n')

        execute('httpie >> %s' % filename, self.context)

        with open(filename) as f:
            content = f.read()
        self.assertEqual(content, 'hello world\nhttp http://localhost')

    def test_httpie_redirect_append_without_spaces(self):
        filename = self.make_tempfile()

        # Write something first to make sure it's an append
        with open(filename, 'w') as f:
            f.write('hello world\n')

        execute('httpie>>%s' % filename, self.context)

        with open(filename) as f:
            content = f.read()
        self.assertEqual(content, 'hello world\nhttp http://localhost')

    def test_httpie_redirect_append_quoted_filename(self):
        filename = self.make_tempfile()

        # Write something first to make sure it's an append
        with open(filename, 'w') as f:
            f.write('hello world\n')

        execute("httpie >> '%s'" % filename, self.context)

        with open(filename) as f:
            content = f.read()
        self.assertEqual(content, 'hello world\nhttp http://localhost')
