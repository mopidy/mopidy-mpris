from __future__ import annotations

import logging
from typing import TYPE_CHECKING

import pydbus

from mopidy_mpris.player import Player
from mopidy_mpris.playlists import Playlists
from mopidy_mpris.root import Root

if TYPE_CHECKING:
    from mopidy.config import Config
    from mopidy.core import CoreProxy

logger = logging.getLogger(__name__)


class Server:
    def __init__(self, config: Config, core: CoreProxy) -> None:
        self.config = config
        self.core = core

        self.root = Root(config, core)
        self.player = Player(config, core)
        self.playlists = Playlists(config, core)

        self._publication_token = None

    def publish(self) -> None:
        bus_type = self.config["mpris"]["bus_type"]  # pyright: ignore[reportGeneralTypeIssues]
        logger.debug("Connecting to D-Bus %s bus...", bus_type)

        bus = pydbus.SystemBus() if bus_type == "system" else pydbus.SessionBus()

        logger.info("MPRIS server connected to D-Bus %s bus", bus_type)

        self._publication_token = bus.publish(
            "org.mpris.MediaPlayer2.mopidy",
            ("/org/mpris/MediaPlayer2", self.root),
            ("/org/mpris/MediaPlayer2", self.player),
            ("/org/mpris/MediaPlayer2", self.playlists),
        )

    def unpublish(self) -> None:
        if self._publication_token:
            self._publication_token.unpublish()
            self._publication_token = None
