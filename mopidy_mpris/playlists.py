"""Implementation of org.mpris.MediaPlayer2.Playlists interface.

https://specifications.freedesktop.org/mpris-spec/2.2/Playlists_Interface.html
"""

from __future__ import unicode_literals

import base64
import logging

from pydbus.generic import signal

from mopidy_mpris.interface import Interface


logger = logging.getLogger(__name__)


class Playlists(Interface):
    """
    <node>
      <interface name="org.mpris.MediaPlayer2.Playlists">
        <method name="ActivatePlaylist">
          <arg name="PlaylistId" type="o" direction="in"/>
        </method>
        <method name="GetPlaylists">
          <arg name="Index" type="u" direction="in"/>
          <arg name="MaxCount" type="u" direction="in"/>
          <arg name="Order" type="s" direction="in"/>
          <arg name="ReverseOrder" type="b" direction="in"/>
          <arg name="Playlists" type="a(oss)" direction="out"/>
        </method>
        <signal name="PlaylistChanged">
          <arg name="Playlist" type="oss"/>
        </signal>
        <property name="PlaylistCount" type="u" access="read"/>
        <property name="Orderings" type="as" access="read"/>
        <property name="ActivePlaylist" type="(b(oss))" access="read"/>
      </interface>
    </node>
    """

    INTERFACE = 'org.mpris.MediaPlayer2.Playlists'

    def ActivatePlaylist(self, playlist_id):
        logger.debug(
            '%s.ActivatePlaylist(%r) called', self.INTERFACE, playlist_id)
        playlist_uri = get_playlist_uri(playlist_id)
        playlist = self.core.playlists.lookup(playlist_uri).get()
        if playlist and playlist.tracks:
            tl_tracks = self.core.tracklist.add(playlist.tracks).get()
            self.core.playback.play(tlid=tl_tracks[0].tlid).get()

    def GetPlaylists(self, index, max_count, order, reverse):
        logger.debug(
            '%s.GetPlaylists(%r, %r, %r, %r) called',
            self.INTERFACE, index, max_count, order, reverse)
        playlists = self.core.playlists.as_list().get()
        if order == 'Alphabetical':
            playlists.sort(key=lambda p: p.name, reverse=reverse)
        elif order == 'User' and reverse:
            playlists.reverse()
        slice_end = index + max_count
        playlists = playlists[index:slice_end]
        results = [
            (get_playlist_id(p.uri), p.name, '')
            for p in playlists]
        return results

    PlaylistChanged = signal()

    @property
    def PlaylistCount(self):
        self.log_trace('Getting %s.PlaylistCount', self.INTERFACE)
        return len(self.core.playlists.as_list().get())

    @property
    def Orderings(self):
        self.log_trace('Getting %s.Orderings', self.INTERFACE)
        return [
            'Alphabetical',  # Order by playlist.name
            'User',          # Don't change order
        ]

    @property
    def ActivePlaylist(self):
        self.log_trace('Getting %s.ActivePlaylist', self.INTERFACE)
        playlist_is_valid = False
        playlist = ('/', 'None', '')
        return (playlist_is_valid, playlist)


def get_playlist_id(playlist_uri):
    # Only A-Za-z0-9_ is allowed, which is 63 chars, so we can't use
    # base64. Luckily, D-Bus does not limit the length of object paths.
    # Since base32 pads trailing bytes with "=" chars, we need to replace
    # them with an allowed character such as "_".
    encoded_uri = base64.b32encode(playlist_uri).replace('=', '_')
    return '/com/mopidy/playlist/%s' % encoded_uri


def get_playlist_uri(playlist_id):
    encoded_uri = playlist_id.split('/')[-1].replace('_', '=')
    return base64.b32decode(encoded_uri)
