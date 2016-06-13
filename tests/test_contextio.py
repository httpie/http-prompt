from .base import TempAppDirTestCase

from http_prompt.context import Context
from http_prompt.contextio import load_context, save_context


class TestContextIO(TempAppDirTestCase):

    def test_save_and_load(self):
        c = Context('http://example.com')
        c.headers['Authorization'] = 'apikey'
        c.querystring_params.update({
            'type': 'any',
            'offset': '100'
        })
        c.options.update({
            '--verify': 'no',
            '--style': 'default',
            '--follow': None
        })

        save_context(c)

        c2 = Context('http://example.com')
        load_context(c2)

        self.assertEqual(c2.headers, c.headers)
        self.assertEqual(c2.querystring_params, c.querystring_params)
        self.assertEqual(c2.body_params, c.body_params)

        # Make sure save_context() didn't save '--style'
        self.assertEqual(c2.options, {
            '--verify': 'no',
            '--follow': None
        })

    def test_different_ports(self):
        c = Context('http://example.com')
        c.headers['Authorization'] = 'apikey'
        c.querystring_params.update({
            'type': 'any',
            'offset': '100'
        })
        c.options.update({
            '--verify': 'no',
            '--style': 'default',
            '--follow': None
        })

        save_context(c)

        c2 = Context('http://example.com:8000')
        load_context(c2)

        self.assertFalse(c2.headers)
        self.assertFalse(c2.querystring_params)
        self.assertFalse(c2.body_params)
        self.assertFalse(c2.options)
