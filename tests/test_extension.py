import unittest
from unittest import mock

from mopidy_mpris import Extension
from mopidy_mpris import frontend as frontend_lib


class ExtensionTest(unittest.TestCase):
    def test_get_default_config(self):
        ext = Extension()

        config = ext.get_default_config()

        assert "[mpris]" in config
        assert "enabled = true" in config
        assert "bus_type = session" in config

    def test_get_config_schema(self):
        ext = Extension()

        schema = ext.get_config_schema()

        assert "desktop_file" in schema
        assert "bus_type" in schema

    def test_get_frontend_classes(self):
        ext = Extension()
        registry = mock.Mock()

        ext.setup(registry)

        registry.add.assert_called_once_with("frontend", frontend_lib.MprisFrontend)
