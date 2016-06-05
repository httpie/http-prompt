import os
import shutil
import stat
import sys
import tempfile
import unittest

from http_prompt import xdg


class TestXDG(unittest.TestCase):

    def setUp(self):
        # Create a temp dir that will contain data and config directories
        self.temp_dir = tempfile.mkdtemp()

        if sys.platform == 'win32':
            self.homes = {
                # subdir_name: envvar_name
                'data': 'LOCALAPPDATA',
                'config': 'LOCALAPPDATA'
            }
        else:
            self.homes = {
                # subdir_name: envvar_name
                'data': 'XDG_DATA_HOME',
                'config': 'XDG_CONFIG_HOME'
            }

        # Used to restore
        self.orig_envvars = {}

        for subdir_name, envvar_name in self.homes.items():
            if envvar_name in os.environ:
                self.orig_envvars[envvar_name] = os.environ[envvar_name]
            os.environ[envvar_name] = os.path.join(self.temp_dir, subdir_name)

    def tearDown(self):
        # Restore envvar values
        for name in self.homes.values():
            if name in self.orig_envvars:
                os.environ[name] = self.orig_envvars[name]
            else:
                del os.environ[name]

        shutil.rmtree(self.temp_dir)

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
