from __future__ import unicode_literals

import logging

import pydbus

from mopidy_mpris.player import Player
from mopidy_mpris.playlists import Playlists
from mopidy_mpris.root import Root


logger = logging.getLogger(__name__)


class Server(object):
    def __init__(self, config, core):
        self.config = config
        self.core = core

        self.root = Root(config, core)
        self.player = Player(config, core)
        self.playlists = Playlists(config, core)

        self._publication_token = None

    def publish(self):
        bus_type = self.config['mpris']['bus_type']
        logger.debug('Connecting to D-Bus %s bus...', bus_type)

        if bus_type == 'system':
            bus = pydbus.SystemBus()
        else:
            bus = pydbus.SessionBus()

        logger.info('MPRIS server connected to D-Bus %s bus', bus_type)

        self._publication_token = bus.publish(
            'org.mpris.MediaPlayer2.mopidy',
            ('/org/mpris/MediaPlayer2', self.root),
            ('/org/mpris/MediaPlayer2', self.player),
            ('/org/mpris/MediaPlayer2', self.playlists),
        )

    def unpublish(self):
        if self._publication_token:
            self._publication_token.unpublish()
            self._publication_token = None
