from __future__ import unicode_literals

import logging

from pydbus.generic import signal


logger = logging.getLogger(__name__)

# This should be kept in sync with mopidy.internal.log.TRACE_LOG_LEVEL
TRACE_LOG_LEVEL = 5


class Interface(object):
    def __init__(self, config, core):
        self.config = config
        self.core = core

    PropertiesChanged = signal()

    def log_trace(self, *args, **kwargs):
        logger.log(TRACE_LOG_LEVEL, *args, **kwargs)
