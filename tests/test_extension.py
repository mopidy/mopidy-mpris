import unittest

import mock

from mopidy_mpris import Extension, frontend as frontend_lib


class ExtensionTest(unittest.TestCase):

    def test_get_default_config(self):
        ext = Extension()

        config = ext.get_default_config()

        self.assertIn('[mpris]', config)
        self.assertIn('enabled = true', config)
        self.assertIn('bus_type = session', config)

    def test_get_config_schema(self):
        ext = Extension()

        schema = ext.get_config_schema()

        self.assertIn('desktop_file', schema)
        self.assertIn('bus_type', schema)

    def test_get_frontend_classes(self):
        ext = Extension()
        registry = mock.Mock()

        ext.setup(registry)

        registry.add.assert_called_once_with(
            'frontend', frontend_lib.MprisFrontend)
