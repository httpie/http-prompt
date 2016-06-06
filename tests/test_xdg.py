import os
import stat

from .base import TempAppDirTestCase
from http_prompt import xdg


class TestXDG(TempAppDirTestCase):

    def test_get_app_data_home(self):
        path = xdg.get_data_dir()
        expected_path = os.path.join(os.environ[self.homes['data']],
                                     'http-prompt')
        self.assertEqual(path, expected_path)

        # Make sure permission for the directory is 700
        mask = stat.S_IMODE(os.stat(path).st_mode)
        self.assertTrue(mask & stat.S_IRWXU)
        self.assertFalse(mask & stat.S_IRWXG)
        self.assertFalse(mask & stat.S_IRWXO)

    def test_get_app_config_home(self):
        path = xdg.get_config_dir()
        expected_path = os.path.join(os.environ[self.homes['config']],
                                     'http-prompt')
        self.assertEqual(path, expected_path)

        # Make sure permission for the directory is 700
        mask = stat.S_IMODE(os.stat(path).st_mode)
        self.assertTrue(mask & stat.S_IRWXU)
        self.assertFalse(mask & stat.S_IRWXG)
        self.assertFalse(mask & stat.S_IRWXO)

    def test_get_resource_data_dir(self):
        path = xdg.get_data_dir('something')
        expected_path = os.path.join(
            os.environ['XDG_DATA_HOME'], 'http-prompt', 'something')
        self.assertEqual(path, expected_path)
        self.assertTrue(os.path.exists(path))

        # Make sure we can write a file to the directory
        with open(os.path.join(path, 'test'), 'wb') as f:
            f.write(b'hello')

    def test_get_resource_config_dir(self):
        path = xdg.get_config_dir('something')
        expected_path = os.path.join(
            os.environ['XDG_CONFIG_HOME'], 'http-prompt', 'something')
        self.assertEqual(path, expected_path)
        self.assertTrue(os.path.exists(path))

        # Make sure we can write a file to the directory
        with open(os.path.join(path, 'test'), 'wb') as f:
            f.write(b'hello')
