"""Implementation of org.mpris.MediaPlayer2 interface.

https://specifications.freedesktop.org/mpris-spec/2.2/Media_Player.html
"""

from __future__ import unicode_literals

import logging

from mopidy_mpris.interface import Interface


logger = logging.getLogger(__name__)


class Root(Interface):
    """
    <node>
      <interface name="org.mpris.MediaPlayer2">
        <method name="Raise"/>
        <method name="Quit"/>
        <property name="CanQuit" type="b" access="read"/>
        <property name="CanRaise" type="b" access="read"/>
        <property name="Fullscreen" type="b" access="readwrite"/>
        <property name="CanSetFullscreen" type="b" access="read"/>
        <property name="HasTrackList" type="b" access="read"/>
        <property name="Identity" type="s" access="read"/>
        <property name="DesktopEntry" type="s" access="read"/>
        <property name="SupportedUriSchemes" type="as" access="read"/>
        <property name="SupportedMimeTypes" type="as" access="read"/>
      </interface>
    </node>
    """

    INTERFACE = 'org.mpris.MediaPlayer2'

    def Raise(self):
        logger.debug('%s.Raise called', self.INTERFACE)
        # Do nothing, as we do not have a GUI

    def Quit(self):
        logger.debug('%s.Quit called', self.INTERFACE)
        # Do nothing, as we do not allow MPRIS clients to shut down Mopidy

    CanQuit = False

    @property
    def Fullscreen(self):
        self.log_trace('Getting %s.Fullscreen', self.INTERFACE)
        return False

    @Fullscreen.setter
    def Fullscreen(self, value):
        logger.debug('Setting %s.Fullscreen to %s', self.INTERFACE, value)
        pass

    CanSetFullscreen = False
    CanRaise = False
    HasTrackList = False  # NOTE Change if adding optional track list support
    Identity = 'Mopidy'

    @property
    def DesktopEntry(self):
        self.log_trace('Getting %s.DesktopEntry', self.INTERFACE)
        # This property is optional to expose. If we set this to "mopidy", the
        # basename of "mopidy.desktop", some MPRIS clients will start a new
        # Mopidy instance in a terminal window if one clicks outside the
        # buttons of the UI. This is probably never what the user wants.
        return ''

    @property
    def SupportedUriSchemes(self):
        self.log_trace('Getting %s.SupportedUriSchemes', self.INTERFACE)
        return self.core.get_uri_schemes().get()

    @property
    def SupportedMimeTypes(self):
        # NOTE Return MIME types supported by local backend if support for
        # reporting supported MIME types is added.
        self.log_trace('Getting %s.SupportedMimeTypes', self.INTERFACE)
        return [
            'audio/mpeg',
            'audio/x-ms-wma',
            'audio/x-ms-asf',
            'audio/x-flac',
            'audio/flac',
            'audio/l16;channels=2;rate=44100',
            'audio/l16;rate=44100;channels=2',
        ]
