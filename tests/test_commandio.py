from .base import TempAppDirTestCase

from http_prompt.commandio import save_file,read_file,put
from http_prompt.outputmethod import OutputMethod

from mock import patch


class TestCommandIO(TempAppDirTestCase):

    def setUp(self):
        super(TestCommandIO, self).setUp()
        self.patchers = [
            ('commandio_click', patch('http_prompt.commandio.click')),
        ]
        for attr_name, patcher in self.patchers:
            setattr(self, attr_name, patcher.start())

        self.data = 'whatever'
        self.filepath = self.temp_dir + '/savetest'

    def tearDown(self):
        super(TestCommandIO, self).tearDown()
        for _, patcher in self.patchers:
            patcher.stop()

    def test_save_and_read(self):

        save_file(self.data, self.filepath)

        saved_data = read_file(self.filepath)

        self.assertEqual(self.data, saved_data)

    def test_put(self):

        #write file and echo
        put(self.data, [OutputMethod.echo, OutputMethod.write_file], self.filepath)
        saved_data = read_file(self.filepath)

        env_text = self.commandio_click.echo_via_pager.call_args[0][0]

        self.assertEqual(self.data, saved_data)
        self.assertEqual(self.data, env_text)

        #append file and echo

        put(self.data, [OutputMethod.echo, OutputMethod.append_file], self.filepath)
        saved_data = read_file(self.filepath)

        env_text = self.commandio_click.echo_via_pager.call_args[0][0]

        self.assertEqual(self.data + '\n' + self.data, saved_data)
        self.assertEqual(self.data, env_text)
