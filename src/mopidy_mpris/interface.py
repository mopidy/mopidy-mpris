import logging
from typing import Any

from mopidy.core import CoreProxy
from pydbus.generic import signal

logger = logging.getLogger(__name__)

# This should be kept in sync with mopidy.internal.log.TRACE_LOG_LEVEL
TRACE_LOG_LEVEL = 5


class Interface:
    def __init__(self, config: dict[str, dict[str, Any]], core: CoreProxy):
        self.config = config
        self.core = core

    PropertiesChanged = signal()

    def log_trace(self, *args, **kwargs):
        logger.log(TRACE_LOG_LEVEL, *args, **kwargs)
