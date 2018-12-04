from __future__ import unicode_literals

import os

from mopidy import config, exceptions, ext


__version__ = '2.0.0'


class Extension(ext.Extension):

    dist_name = 'Mopidy-MPRIS'
    ext_name = 'mpris'
    version = __version__

    def get_default_config(self):
        conf_file = os.path.join(os.path.dirname(__file__), 'ext.conf')
        return config.read(conf_file)

    def get_config_schema(self):
        schema = super(Extension, self).get_config_schema()
        schema['desktop_file'] = config.Deprecated()
        schema['bus_type'] = config.String(choices=['session', 'system'])
        return schema

    def validate_environment(self):
        try:
            import pydbus  # noqa
        except ImportError as e:
            raise exceptions.ExtensionError('pydbus library not found', e)

    def setup(self, registry):
        from .frontend import MprisFrontend
        registry.add('frontend', MprisFrontend)
