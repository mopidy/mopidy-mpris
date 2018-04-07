from __future__ import unicode_literals

from pydbus.generic import signal


class Interface(object):
    def __init__(self, config, core):
        self.config = config
        self.core = core

    PropertiesChanged = signal()
