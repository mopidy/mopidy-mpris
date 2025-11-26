import pathlib
from importlib.metadata import version

from mopidy import config, exceptions, ext

__version__ = version("mopidy-mpris")


class Extension(ext.Extension):
    dist_name = "mopidy-mpris"
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
            import pydbus  # noqa: F401, PLC0415
        except ImportError as exc:
            msg = "pydbus library not found"
            raise exceptions.ExtensionError(msg, exc) from exc

    def setup(self, registry):
        from mopidy_mpris.frontend import MprisFrontend  # noqa: PLC0415

        registry.add("frontend", MprisFrontend)
