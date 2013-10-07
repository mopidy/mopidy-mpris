import unittest

from mopidy_mpris import Extension, frontend as frontend_lib


class ExtensionTest(unittest.TestCase):

    def test_get_default_config(self):
        ext = Extension()

        config = ext.get_default_config()

        self.assertIn('[mpris]', config)
        self.assertIn('enabled = true', config)

    def test_get_config_schema(self):
        ext = Extension()

        schema = ext.get_config_schema()

        self.assertIn('desktop_file', schema)

    def test_get_frontend_classes(self):
        ext = Extension()

        frontends = ext.get_frontend_classes()

        self.assertIn(frontend_lib.MprisFrontend, frontends)
