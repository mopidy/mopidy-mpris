import pathlib

import pkg_resources

from mopidy import config, exceptions, ext

__version__ = pkg_resources.get_distribution("Mopidy-MPRIS").version


class Extension(ext.Extension):

    dist_name = "Mopidy-MPRIS"
    ext_name = "mpris"
    version = __version__

    def get_default_config(self):
        return config.read(pathlib.Path(__file__).parent / "ext.conf")

    def get_config_schema(self):
        schema = super().get_config_schema()
        schema["desktop_file"] = config.Deprecated()
        schema["bus_type"] = config.String(choices=["session", "system"])
        return schema

    def validate_environment(self):
        try:
            import pydbus  # noqa
        except ImportError as e:
            raise exceptions.ExtensionError("pydbus library not found", e)

    def setup(self, registry):
        from .frontend import MprisFrontend

        registry.add("frontend", MprisFrontend)
