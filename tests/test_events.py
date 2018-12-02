from __future__ import unicode_literals

import mock

from mopidy.core.playback import PlaybackState
from mopidy.models import Playlist, TlTrack

import pytest

from mopidy_mpris import (
    frontend as frontend_mod, player, playlists, root, server)


@pytest.fixture
def frontend():
    # As a plain class, not an actor:
    result = frontend_mod.MprisFrontend(config=None, core=None)
    result.mpris = mock.Mock(spec=server.Server)
    result.mpris.root = mock.Mock(spec=root.Root)
    result.mpris.root.INTERFACE = root.Root.INTERFACE
    result.mpris.player = mock.Mock(spec=player.Player)
    result.mpris.player.INTERFACE = player.Player.INTERFACE
    result.mpris.playlists = mock.Mock(spec=playlists.Playlists)
    result.mpris.playlists.INTERFACE = playlists.Playlists.INTERFACE
    return result


def test_track_playback_paused_event_changes_playback_status(frontend):
    frontend.mpris.player.PlaybackStatus = 'Paused'

    frontend.track_playback_paused(
        tl_track=TlTrack(), time_position=0)

    frontend.mpris.player.PropertiesChanged.assert_called_with(
        player.Player.INTERFACE, {'PlaybackStatus': 'Paused'}, [])


def test_track_playback_resumed_event_changes_playback_status(frontend):
    frontend.mpris.player.PlaybackStatus = 'Playing'

    frontend.track_playback_resumed(
        tl_track=TlTrack(), time_position=0)

    frontend.mpris.player.PropertiesChanged.assert_called_with(
        player.Player.INTERFACE, {'PlaybackStatus': 'Playing'}, [])


def test_track_playback_started_changes_playback_status_and_metadata(frontend):
    frontend.mpris.player.Metadata = '...'
    frontend.mpris.player.PlaybackStatus = 'Playing'

    frontend.track_playback_started(tl_track=TlTrack())

    frontend.mpris.player.PropertiesChanged.assert_called_with(
        player.Player.INTERFACE,
        {'Metadata': '...', 'PlaybackStatus': 'Playing'}, [])


def test_track_playback_ended_changes_playback_status_and_metadata(frontend):
    frontend.mpris.player.Metadata = '...'
    frontend.mpris.player.PlaybackStatus = 'Stopped'

    frontend.track_playback_ended(
        tl_track=TlTrack(), time_position=0)

    frontend.mpris.player.PropertiesChanged.assert_called_with(
        player.Player.INTERFACE,
        {'Metadata': '...', 'PlaybackStatus': 'Stopped'}, [])


def test_playback_state_changed_changes_playback_status_and_metadata(frontend):
    frontend.mpris.player.Metadata = '...'
    frontend.mpris.player.PlaybackStatus = 'Stopped'

    frontend.playback_state_changed(
        PlaybackState.PLAYING, PlaybackState.STOPPED)

    frontend.mpris.player.PropertiesChanged.assert_called_with(
        player.Player.INTERFACE,
        {'Metadata': '...', 'PlaybackStatus': 'Stopped'}, [])


def test_playlists_loaded_event_changes_playlist_count(frontend):
    frontend.mpris.playlists.PlaylistCount = 17

    frontend.playlists_loaded()

    frontend.mpris.playlists.PropertiesChanged.assert_called_with(
        playlists.Playlists.INTERFACE, {'PlaylistCount': 17}, [])


def test_playlist_changed_event_causes_mpris_playlist_changed_event(frontend):
    playlist = Playlist(uri='dummy:foo', name='foo')

    frontend.playlist_changed(playlist=playlist)

    frontend.mpris.playlists.PlaylistChanged.assert_called_with(
        '/com/mopidy/playlist/MR2W23LZHJTG63Y_', 'foo', '')


def test_playlist_deleted_event_changes_playlist_count(frontend):
    frontend.mpris.playlists.PlaylistCount = 17

    frontend.playlist_deleted('dummy:foo')

    frontend.mpris.playlists.PropertiesChanged.assert_called_with(
        playlists.Playlists.INTERFACE, {'PlaylistCount': 17}, [])


def test_options_changed_event_changes_loopstatus_and_shuffle(frontend):
    frontend.mpris.player.CanGoPrevious = False
    frontend.mpris.player.CanGoNext = True
    frontend.mpris.player.LoopStatus = 'Track'
    frontend.mpris.player.Shuffle = True

    frontend.options_changed()

    frontend.mpris.player.PropertiesChanged.assert_called_with(
        player.Player.INTERFACE,
        {
             'LoopStatus': 'Track',
             'Shuffle': True,
             'CanGoPrevious': False,
             'CanGoNext': True,
        },
        []
    )


def test_volume_changed_event_changes_volume(frontend):
    frontend.mpris.player.Volume = 1.0

    frontend.volume_changed(volume=100)

    frontend.mpris.player.PropertiesChanged.assert_called_with(
        player.Player.INTERFACE, {'Volume': 1.0}, [])


def test_mute_changed_event_changes_volume(frontend):
    frontend.mpris.player.Volume = 0.0

    frontend.mute_changed(True)

    frontend.mpris.player.PropertiesChanged.assert_called_with(
        player.Player.INTERFACE, {'Volume': 0.0}, [])


def test_seeked_event_causes_mpris_seeked_event(frontend):
    frontend.seeked(time_position=31000)

    frontend.mpris.player.Seeked.assert_called_with(31000000)


def test_stream_title_changed_changes_metadata(frontend):
    frontend.mpris.player.Metadata = '...'

    frontend.stream_title_changed('a new title')

    frontend.mpris.player.PropertiesChanged.assert_called_with(
        player.Player.INTERFACE, {'Metadata': '...'}, [])
