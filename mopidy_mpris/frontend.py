from __future__ import unicode_literals

import logging

from mopidy.core import CoreListener

import pykka

from mopidy_mpris.playlists import get_playlist_id
from mopidy_mpris.server import Server


logger = logging.getLogger(__name__)


class MprisFrontend(pykka.ThreadingActor, CoreListener):
    def __init__(self, config, core):
        super(MprisFrontend, self).__init__()
        self.config = config
        self.core = core
        self.mpris = None

    def on_start(self):
        try:
            self.mpris = Server(self.config, self.core)
            self.mpris.publish()
        except Exception as e:
            logger.warning('MPRIS frontend setup failed (%s)', e)
            self.stop()

    def on_stop(self):
        logger.debug('Removing MPRIS object from D-Bus connection...')
        if self.mpris:
            self.mpris.unpublish()
            self.mpris = None
        logger.debug('Removed MPRIS object from D-Bus connection')

    def track_playback_paused(self, tl_track, time_position):
        logger.debug('Received track_playback_paused event')
        if self.mpris is None:
            return
        _emit_properties_changed(self.mpris.player, ['PlaybackStatus'])

    def track_playback_resumed(self, tl_track, time_position):
        logger.debug('Received track_playback_resumed event')
        if self.mpris is None:
            return
        _emit_properties_changed(self.mpris.player, ['PlaybackStatus'])

    def track_playback_started(self, tl_track):
        logger.debug('Received track_playback_started event')
        if self.mpris is None:
            return
        _emit_properties_changed(
            self.mpris.player, ['PlaybackStatus', 'Metadata'])

    def track_playback_ended(self, tl_track, time_position):
        logger.debug('Received track_playback_ended event')
        if self.mpris is None:
            return
        _emit_properties_changed(
            self.mpris.player, ['PlaybackStatus', 'Metadata'])

    def volume_changed(self, volume):
        logger.debug('Received volume_changed event')
        if self.mpris is None:
            return
        _emit_properties_changed(self.mpris.player, ['Volume'])

    def seeked(self, time_position):
        logger.debug('Received seeked event')
        if self.mpris is None:
            return
        time_position_in_microseconds = time_position * 1000
        self.mpris.player.Seeked(time_position_in_microseconds)

    def playlists_loaded(self):
        logger.debug('Received playlists_loaded event')
        _emit_properties_changed(self.mpris.playlists, ['PlaylistCount'])

    def playlist_changed(self, playlist):
        logger.debug('Received playlist_changed event')
        if self.mpris is None:
            return
        playlist_id = get_playlist_id(playlist.uri)
        playlist = (playlist_id, playlist.name, '')
        self.mpris.playlists.PlaylistChanged(playlist)


def _emit_properties_changed(interface, changed_properties):
    props_with_new_values = [
        (p, getattr(interface, p))
        for p in changed_properties]
    interface.PropertiesChanged(
        interface.INTERFACE, dict(props_with_new_values), [])
