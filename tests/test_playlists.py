from __future__ import unicode_literals

from mopidy.audio import PlaybackState
from mopidy.models import Track

import pytest

from mopidy_mpris.playlists import Playlists


@pytest.fixture
def dummy_playlists(core):
    result = {}

    for name, lm in [('foo', 3000000), ('bar', 2000000), ('baz', 1000000)]:
        pl = core.playlists.create(name).get()
        pl = pl.replace(last_modified=lm)
        result[name] = core.playlists.save(pl).get()

    return result


@pytest.fixture
def playlists(config, core, dummy_playlists):
    return Playlists(config, core)


def test_activate_playlist_appends_tracks_to_tracklist(
        core, playlists, dummy_playlists):
    core.tracklist.add([
        Track(uri='dummy:old-a'),
        Track(uri='dummy:old-b'),
    ])
    assert core.tracklist.get_length().get() == 2

    pl = dummy_playlists['baz']
    pl = pl.replace(tracks=[
        Track(uri='dummy:baz-a'),
        Track(uri='dummy:baz-b'),
        Track(uri='dummy:baz-c'),
    ])
    pl = core.playlists.save(pl).get()
    playlist_id = playlists.GetPlaylists(0, 100, 'User', False)[2][0]

    playlists.ActivatePlaylist(playlist_id)

    assert core.tracklist.get_length().get() == 5
    assert core.playback.get_state().get() == PlaybackState.PLAYING
    assert core.playback.get_current_track().get() == pl.tracks[0]


def test_activate_empty_playlist_is_harmless(core, playlists):
    assert core.tracklist.get_length().get() == 0
    playlist_id = playlists.GetPlaylists(0, 100, 'User', False)[2][0]

    playlists.ActivatePlaylist(playlist_id)

    assert core.tracklist.get_length().get() == 0
    assert core.playback.get_state().get() == PlaybackState.STOPPED
    assert core.playback.get_current_track().get() is None


def test_get_playlists_in_alphabetical_order(playlists):
    result = playlists.GetPlaylists(0, 100, 'Alphabetical', False)

    assert result == [
        ('/com/mopidy/playlist/MR2W23LZHJRGC4Q_', 'bar', ''),
        ('/com/mopidy/playlist/MR2W23LZHJRGC6Q_', 'baz', ''),
        ('/com/mopidy/playlist/MR2W23LZHJTG63Y_', 'foo', ''),
    ]


def test_get_playlists_in_reverse_alphabetical_order(playlists):
    result = playlists.GetPlaylists(0, 100, 'Alphabetical', True)

    assert len(result) == 3
    assert result[0][1] == 'foo'
    assert result[1][1] == 'baz'
    assert result[2][1] == 'bar'


def test_get_playlists_in_user_order(playlists):
    result = playlists.GetPlaylists(0, 100, 'User', False)

    assert len(result) == 3
    assert result[0][1] == 'foo'
    assert result[1][1] == 'bar'
    assert result[2][1] == 'baz'


def test_get_playlists_in_reverse_user_order(playlists):
    result = playlists.GetPlaylists(0, 100, 'User', True)

    assert len(result) == 3
    assert result[0][1] == 'baz'
    assert result[1][1] == 'bar'
    assert result[2][1] == 'foo'


def test_get_playlists_slice_on_start_of_list(playlists):
    result = playlists.GetPlaylists(0, 2, 'User', False)

    assert len(result) == 2
    assert result[0][1] == 'foo'
    assert result[1][1] == 'bar'


def test_get_playlists_slice_later_in_list(playlists):
    result = playlists.GetPlaylists(2, 2, 'User', False)

    assert len(result) == 1
    assert result[0][1] == 'baz'


def test_get_playlist_count_returns_number_of_playlists(playlists):
    assert playlists.PlaylistCount == 3


def test_get_orderings_includes_alpha_modified_and_user(playlists):
    result = playlists.Orderings

    assert 'Alphabetical' in result
    assert 'Created' not in result
    assert 'Modified' not in result
    assert 'Played' not in result
    assert 'User' in result


def test_get_active_playlist_does_not_return_a_playlist(playlists):
    result = playlists.ActivePlaylist

    valid, playlist = result
    playlist_id, playlist_name, playlist_icon_uri = playlist

    assert valid is False
    assert playlist_id == '/'
    assert playlist_name == 'None'
    assert playlist_icon_uri == ''
