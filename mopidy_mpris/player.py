"""Implementation of org.mpris.MediaPlayer2.Player interface.

https://specifications.freedesktop.org/mpris-spec/2.2/Player_Interface.html
"""

from __future__ import unicode_literals

import logging

from gi.repository.GLib import Variant

from mopidy.core import PlaybackState

from pydbus.generic import signal

from mopidy_mpris.interface import Interface


logger = logging.getLogger(__name__)


class Player(Interface):
    """
    <node>
      <interface name="org.mpris.MediaPlayer2.Player">
        <method name="Next"/>
        <method name="Previous"/>
        <method name="Pause"/>
        <method name="PlayPause"/>
        <method name="Stop"/>
        <method name="Play"/>
        <method name="Seek">
          <arg name="Offset" type="x" direction="in"/>
        </method>
        <method name="SetPosition">
          <arg name="TrackId" type="o" direction="in"/>
          <arg name="Position" type="x" direction="in"/>
        </method>
        <method name="OpenUri">
          <arg name="Uri" type="s" direction="in"/>
        </method>
        <signal name="Seeked">
          <arg name="Position" type="x"/>
        </signal>
        <property name="PlaybackStatus" type="s" access="read"/>
        <property name="LoopStatus" type="s" access="readwrite"/>
        <property name="Rate" type="d" access="readwrite"/>
        <property name="Shuffle" type="b" access="readwrite"/>
        <property name="Metadata" type="a{sv}" access="read"/>
        <property name="Volume" type="d" access="readwrite"/>
        <property name="Position" type="x" access="read"/>
        <property name="MinimumRate" type="d" access="read"/>
        <property name="MaximumRate" type="d" access="read"/>
        <property name="CanGoNext" type="b" access="read"/>
        <property name="CanGoPrevious" type="b" access="read"/>
        <property name="CanPlay" type="b" access="read"/>
        <property name="CanPause" type="b" access="read"/>
        <property name="CanSeek" type="b" access="read"/>
        <property name="CanControl" type="b" access="read"/>
      </interface>
    </node>
    """

    INTERFACE = 'org.mpris.MediaPlayer2.Player'

    # To override from tests.
    _CanControl = True

    def Next(self):
        logger.debug('%s.Next called', self.INTERFACE)
        if not self.CanGoNext:
            logger.debug('%s.Next not allowed', self.INTERFACE)
            return
        self.core.playback.next().get()

    def Previous(self):
        logger.debug('%s.Previous called', self.INTERFACE)
        if not self.CanGoPrevious:
            logger.debug('%s.Previous not allowed', self.INTERFACE)
            return
        self.core.playback.previous().get()

    def Pause(self):
        logger.debug('%s.Pause called', self.INTERFACE)
        if not self.CanPause:
            logger.debug('%s.Pause not allowed', self.INTERFACE)
            return
        self.core.playback.pause().get()

    def PlayPause(self):
        logger.debug('%s.PlayPause called', self.INTERFACE)
        if not self.CanPause:
            logger.debug('%s.PlayPause not allowed', self.INTERFACE)
            return
        state = self.core.playback.get_state().get()
        if state == PlaybackState.PLAYING:
            self.core.playback.pause().get()
        elif state == PlaybackState.PAUSED:
            self.core.playback.resume().get()
        elif state == PlaybackState.STOPPED:
            self.core.playback.play().get()

    def Stop(self):
        logger.debug('%s.Stop called', self.INTERFACE)
        if not self.CanControl:
            logger.debug('%s.Stop not allowed', self.INTERFACE)
            return
        self.core.playback.stop().get()

    def Play(self):
        logger.debug('%s.Play called', self.INTERFACE)
        if not self.CanPlay:
            logger.debug('%s.Play not allowed', self.INTERFACE)
            return
        state = self.core.playback.get_state().get()
        if state == PlaybackState.PAUSED:
            self.core.playback.resume().get()
        else:
            self.core.playback.play().get()

    def Seek(self, offset):
        logger.debug('%s.Seek called', self.INTERFACE)
        if not self.CanSeek:
            logger.debug('%s.Seek not allowed', self.INTERFACE)
            return
        offset_in_milliseconds = offset // 1000
        current_position = self.core.playback.get_time_position().get()
        new_position = current_position + offset_in_milliseconds
        if new_position < 0:
            new_position = 0
        self.core.playback.seek(new_position).get()

    def SetPosition(self, track_id, position):
        logger.debug('%s.SetPosition called', self.INTERFACE)
        if not self.CanSeek:
            logger.debug('%s.SetPosition not allowed', self.INTERFACE)
            return
        position = position // 1000
        current_tl_track = self.core.playback.get_current_tl_track().get()
        if current_tl_track is None:
            return
        if track_id != get_track_id(current_tl_track.tlid):
            return
        if position < 0:
            return
        if current_tl_track.track.length < position:
            return
        self.core.playback.seek(position).get()

    def OpenUri(self, uri):
        logger.debug('%s.OpenUri called', self.INTERFACE)
        if not self.CanControl:
            # NOTE The spec does not explicitly require this check, but
            # guarding the other methods doesn't help much if OpenUri is open
            # for use.
            logger.debug('%s.OpenUri not allowed', self.INTERFACE)
            return
        # NOTE Check if URI has MIME type known to the backend, if MIME support
        # is added to the backend.
        tl_tracks = self.core.tracklist.add(uri=uri).get()
        if tl_tracks:
            self.core.playback.play(tlid=tl_tracks[0].tlid).get()
        else:
            logger.debug('Track with URI "%s" not found in library.', uri)

    Seeked = signal()

    @property
    def PlaybackStatus(self):
        self.log_trace('Getting %s.PlaybackStatus', self.INTERFACE)
        state = self.core.playback.get_state().get()
        if state == PlaybackState.PLAYING:
            return 'Playing'
        elif state == PlaybackState.PAUSED:
            return 'Paused'
        elif state == PlaybackState.STOPPED:
            return 'Stopped'

    @property
    def LoopStatus(self):
        self.log_trace('Getting %s.LoopStatus', self.INTERFACE)
        repeat = self.core.tracklist.get_repeat().get()
        single = self.core.tracklist.get_single().get()
        if not repeat:
            return 'None'
        else:
            if single:
                return 'Track'
            else:
                return 'Playlist'

    @LoopStatus.setter
    def LoopStatus(self, value):
        if not self.CanControl:
            logger.debug('Setting %s.LoopStatus not allowed', self.INTERFACE)
            return
        logger.debug('Setting %s.LoopStatus to %s', self.INTERFACE, value)
        if value == 'None':
            self.core.tracklist.set_repeat(False)
            self.core.tracklist.set_single(False)
        elif value == 'Track':
            self.core.tracklist.set_repeat(True)
            self.core.tracklist.set_single(True)
        elif value == 'Playlist':
            self.core.tracklist.set_repeat(True)
            self.core.tracklist.set_single(False)

    @property
    def Rate(self):
        self.log_trace('Getting %s.Rate', self.INTERFACE)
        return 1.0

    @Rate.setter
    def Rate(self, value):
        if not self.CanControl:
            # NOTE The spec does not explicitly require this check, but it was
            # added to be consistent with all the other property setters.
            logger.debug('Setting %s.Rate not allowed', self.INTERFACE)
            return
        logger.debug('Setting %s.Rate to %s', self.INTERFACE, value)
        if value == 0:
            self.Pause()

    @property
    def Shuffle(self):
        self.log_trace('Getting %s.Shuffle', self.INTERFACE)
        return self.core.tracklist.get_random().get()

    @Shuffle.setter
    def Shuffle(self, value):
        if not self.CanControl:
            logger.debug('Setting %s.Shuffle not allowed', self.INTERFACE)
            return
        logger.debug('Setting %s.Shuffle to %s', self.INTERFACE, value)
        self.core.tracklist.set_random(bool(value))

    @property
    def Metadata(self):
        self.log_trace('Getting %s.Metadata', self.INTERFACE)
        current_tl_track = self.core.playback.get_current_tl_track().get()
        stream_title = self.core.playback.get_stream_title().get()
        if current_tl_track is None:
            return {}
        else:
            (tlid, track) = current_tl_track
            track_id = get_track_id(tlid)
            res = {'mpris:trackid': Variant('o', track_id)}
            if track.length:
                res['mpris:length'] = Variant('x', track.length * 1000)
            if track.uri:
                res['xesam:url'] = Variant('s', track.uri)
            if stream_title or track.name:
                res['xesam:title'] = Variant('s', stream_title or track.name)
            if track.artists:
                artists = list(track.artists)
                artists.sort(key=lambda a: a.name)
                res['xesam:artist'] = Variant(
                    'as', [a.name for a in artists if a.name])
            if track.album and track.album.name:
                res['xesam:album'] = Variant('s', track.album.name)
            if track.album and track.album.artists:
                artists = list(track.album.artists)
                artists.sort(key=lambda a: a.name)
                res['xesam:albumArtist'] = Variant(
                    'as', [a.name for a in artists if a.name])
            art_url = self._get_art_url(track)
            if art_url:
                res['mpris:artUrl'] = Variant('s', art_url)
            if track.disc_no:
                res['xesam:discNumber'] = Variant('i', track.disc_no)
            if track.track_no:
                res['xesam:trackNumber'] = Variant('i', track.track_no)
            return res

    def _get_art_url(self, track):
        if track.album and track.album.images:
            url = sorted(track.album.images)[0]
            if url:
                return url

        images = self.core.library.get_images([track.uri]).get()
        if images[track.uri]:
            largest_image = sorted(
                images[track.uri], key=lambda i: i.width, reverse=True
            )[0]
            return largest_image.uri

    @property
    def Volume(self):
        self.log_trace('Getting %s.Volume', self.INTERFACE)
        mute = self.core.mixer.get_mute().get()
        volume = self.core.mixer.get_volume().get()
        if volume is None or mute is True:
            return 0
        return volume / 100.0

    @Volume.setter
    def Volume(self, value):
        if not self.CanControl:
            logger.debug('Setting %s.Volume not allowed', self.INTERFACE)
            return
        logger.debug('Setting %s.Volume to %s', self.INTERFACE, value)
        if value is None:
            return
        if value < 0:
            value = 0
        elif value > 1:
            value = 1
        self.core.mixer.set_volume(int(value * 100))
        if value > 0:
            self.core.mixer.set_mute(False)

    @property
    def Position(self):
        self.log_trace('Getting %s.Position', self.INTERFACE)
        return self.core.playback.get_time_position().get() * 1000

    MinimumRate = 1.0
    MaximumRate = 1.0

    @property
    def CanGoNext(self):
        self.log_trace('Getting %s.CanGoNext', self.INTERFACE)
        if not self.CanControl:
            return False
        current_tlid = self.core.playback.get_current_tlid().get()
        next_tlid = self.core.tracklist.get_next_tlid().get()
        return next_tlid != current_tlid

    @property
    def CanGoPrevious(self):
        self.log_trace('Getting %s.CanGoPrevious', self.INTERFACE)
        if not self.CanControl:
            return False
        current_tlid = self.core.playback.get_current_tlid().get()
        previous_tlid = self.core.tracklist.get_previous_tlid().get()
        return previous_tlid != current_tlid

    @property
    def CanPlay(self):
        self.log_trace('Getting %s.CanPlay', self.INTERFACE)
        if not self.CanControl:
            return False
        current_tlid = self.core.playback.get_current_tlid().get()
        next_tlid = self.core.tracklist.get_next_tlid().get()
        return current_tlid is not None or next_tlid is not None

    @property
    def CanPause(self):
        self.log_trace('Getting %s.CanPause', self.INTERFACE)
        if not self.CanControl:
            return False
        # NOTE Should be changed to vary based on capabilities of the current
        # track if Mopidy starts supporting non-seekable media, like streams.
        return True

    @property
    def CanSeek(self):
        self.log_trace('Getting %s.CanSeek', self.INTERFACE)
        if not self.CanControl:
            return False
        # NOTE Should be changed to vary based on capabilities of the current
        # track if Mopidy starts supporting non-seekable media, like streams.
        return True

    @property
    def CanControl(self):
        # NOTE This could be a setting for the end user to change.
        return self._CanControl


def get_track_id(tlid):
    return '/com/mopidy/track/%d' % tlid


def get_track_tlid(track_id):
    assert track_id.startswith('/com/mopidy/track/')
    return track_id.split('/')[-1]
