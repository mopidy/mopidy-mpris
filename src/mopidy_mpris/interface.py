from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any, ClassVar

from pydbus.generic import signal

if TYPE_CHECKING:
    from mopidy.config import Config
    from mopidy.core import CoreProxy

logger = logging.getLogger(__name__)

# This should be kept in sync with mopidy.internal.log.TRACE_LOG_LEVEL
TRACE_LOG_LEVEL = 5


class Interface:
    INTERFACE: ClassVar[str]

    def __init__(self, config: Config, core: CoreProxy) -> None:
        self.config = config
        self.core = core

    PropertiesChanged = signal()

    def log_trace(self, *args: Any, **kwargs: Any) -> None:  # noqa: ANN401
        logger.log(TRACE_LOG_LEVEL, *args, **kwargs)
