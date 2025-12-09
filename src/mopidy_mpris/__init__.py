import pathlib
from importlib.metadata import version

from mopidy import config, exceptions, ext
from mopidy.config import ConfigSchema

__version__ = version("mopidy-mpris")


class Extension(ext.Extension):
    dist_name = "mopidy-mpris"
    ext_name = "mpris"
    version = __version__

    def get_default_config(self) -> str:
        return config.read(pathlib.Path(__file__).parent / "ext.conf")

    def get_config_schema(self) -> ConfigSchema:
        schema = super().get_config_schema()
        schema["desktop_file"] = config.Deprecated()
        schema["bus_type"] = config.String(choices=["session", "system"])
        return schema

    def validate_environment(self) -> None:
        try:
            import pydbus  # noqa: F401, PLC0415
        except ImportError as exc:
            msg = "pydbus library not found"
            raise exceptions.ExtensionError(msg, exc) from exc

    def setup(self, registry: ext.Registry) -> None:
        from mopidy_mpris.frontend import MprisFrontend  # noqa: PLC0415

        registry.add("frontend", MprisFrontend)
