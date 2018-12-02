from __future__ import unicode_literals

from gi.repository import GLib

from mopidy.core import PlaybackState
from mopidy.models import Album, Artist, Image, Track

import pytest

from mopidy_mpris.player import Player


PLAYING = PlaybackState.PLAYING
PAUSED = PlaybackState.PAUSED
STOPPED = PlaybackState.STOPPED


@pytest.fixture
def player(config, core):
    return Player(config, core)


@pytest.mark.parametrize('state, expected', [
    (PLAYING, 'Playing'),
    (PAUSED, 'Paused'),
    (STOPPED, 'Stopped'),
])
def test_get_playback_status(core, player, state, expected):
    core.playback.set_state(state)

    assert player.PlaybackStatus == expected


@pytest.mark.parametrize('repeat, single, expected', [
    (False, False, 'None'),
    (False, True, 'None'),
    (True, False, 'Playlist'),
    (True, True, 'Track'),
])
def test_get_loop_status(core, player, repeat, single, expected):
    core.tracklist.set_repeat(repeat)
    core.tracklist.set_single(single)

    assert player.LoopStatus == expected


@pytest.mark.parametrize('status, expected_repeat, expected_single', [
    ('None', False, False),
    ('Track', True, True),
    ('Playlist', True, False),
])
def test_set_loop_status(
        core, player, status, expected_repeat, expected_single):
    player.LoopStatus = status

    assert core.tracklist.get_repeat().get() is expected_repeat
    assert core.tracklist.get_single().get() is expected_single


def test_set_loop_status_is_ignored_if_can_control_is_false(core, player):
    player._CanControl = False
    core.tracklist.set_repeat(True)
    core.tracklist.set_single(True)

    player.LoopStatus = 'None'

    assert core.tracklist.get_repeat().get() is True
    assert core.tracklist.get_single().get() is True


def test_get_rate_is_greater_or_equal_than_minimum_rate(player):
    assert player.Rate >= player.MinimumRate


def test_get_rate_is_less_or_equal_than_maximum_rate(player):
    assert player.Rate <= player.MaximumRate


def test_set_rate_to_zero_pauses_playback(core, player):
    core.tracklist.add([Track(uri='dummy:a'), Track(uri='dummy:b')])
    core.playback.play().get()
    assert core.playback.get_state().get() == PLAYING

    player.Rate = 0

    assert core.playback.get_state().get() == PAUSED


def test_set_rate_is_ignored_if_can_control_is_false(core, player):
    player._CanControl = False
    core.tracklist.add([Track(uri='dummy:a'), Track(uri='dummy:b')])
    core.playback.play().get()
    assert core.playback.get_state().get() == PLAYING

    player.Rate == 0

    assert core.playback.get_state().get() == PLAYING


@pytest.mark.parametrize('random', [True, False])
def test_get_shuffle(core, player, random):
    core.tracklist.set_random(random)

    assert player.Shuffle is random


@pytest.mark.parametrize('value', [True, False])
def test_set_shuffle(core, player, value):
    core.tracklist.set_random(not value)
    assert core.tracklist.get_random().get() is not value

    player.Shuffle = value

    assert core.tracklist.get_random().get() is value


def test_set_shuffle_is_ignored_if_can_control_is_false(core, player):
    player._CanControl = False
    core.tracklist.set_random(False)

    player.Shuffle = True

    assert core.tracklist.get_random().get() is False


def test_get_metadata_is_empty_when_no_current_track(player):
    assert player.Metadata == {}


def test_get_metadata(core, player):
    core.tracklist.add([Track(
        uri='dummy:a',
        length=3600000,
        name='a',
        artists=[Artist(name='b'), Artist(name='c'), Artist(name=None)],
        album=Album(
            name='d',
            artists=[Artist(name='e'), Artist(name=None)],
        ),
    )])
    core.playback.play().get()

    (tlid, track) = core.playback.get_current_tl_track().get()

    result = player.Metadata

    assert result['mpris:trackid'] == GLib.Variant(
        'o', '/com/mopidy/track/%d' % tlid)
    assert result['mpris:length'] == GLib.Variant('x', 3600000000)
    assert result['xesam:url'] == GLib.Variant('s', 'dummy:a')
    assert result['xesam:title'] == GLib.Variant('s', 'a')
    assert result['xesam:artist'] == GLib.Variant('as', ['b', 'c'])
    assert result['xesam:album'] == GLib.Variant('s', 'd')
    assert result['xesam:albumArtist'] == GLib.Variant('as', ['e'])


def test_get_metadata_prefers_stream_title_over_track_name(
        audio, core, player):
    core.tracklist.add([Track(
        uri='dummy:a',
        name='Track name',
    )])
    core.playback.play().get()

    result = player.Metadata
    assert result['xesam:title'] == GLib.Variant('s', 'Track name')

    audio.trigger_fake_tags_changed({
        'organization': ['Required for Mopidy core to care about the title'],
        'title': ['Stream title'],
    }).get()

    result = player.Metadata
    assert result['xesam:title'] == GLib.Variant('s', 'Stream title')


def test_get_metadata_use_first_album_image_as_art_url(core, player):
    # XXX Currently, the album image order isn't preserved because they
    # are stored as a frozenset(). We pick the first in the set, which is
    # sorted alphabetically, thus we get 'bar.jpg', not 'foo.jpg', which
    # would probably make more sense.
    core.tracklist.add([Track(
        uri='dummy:a',
        album=Album(images=[
            'http://example.com/foo.jpg',
            'http://example.com/bar.jpg',
        ]),
    )])
    core.playback.play().get()

    result = player.Metadata

    assert result['mpris:artUrl'] == GLib.Variant(
        's', 'http://example.com/bar.jpg')


def test_get_metadata_use_library_image_as_art_url(backend, core, player):
    backend.library.dummy_get_images_result = {
        'dummy:a': [
            Image(uri='http://example.com/small.jpg', width=100, height=100),
            Image(uri='http://example.com/large.jpg', width=200, height=200),
        ],
    }
    core.tracklist.add([Track(uri='dummy:a')])
    core.playback.play().get()

    result = player.Metadata

    assert result['mpris:artUrl'] == GLib.Variant(
        's', 'http://example.com/large.jpg')


def test_get_metadata_has_no_art_url_if_no_album(core, player):
    core.tracklist.add([Track(uri='dummy:a')])
    core.playback.play().get()

    assert 'mpris:artUrl' not in player.Metadata


def test_get_metadata_has_no_art_url_if_no_album_images(core, player):
    core.tracklist.add([Track(uri='dummy:a', album=Album(images=[]))])
    core.playback.play().get()

    assert 'mpris:artUrl' not in player.Metadata


def test_get_metadata_has_disc_number_in_album(core, player):
    core.tracklist.add([Track(uri='dummy:a', disc_no=2)])
    core.playback.play().get()

    assert player.Metadata['xesam:discNumber'] == GLib.Variant('i', 2)


def test_get_metadata_has_track_number_in_album(core, player):
    core.tracklist.add([Track(uri='dummy:a', track_no=7)])
    core.playback.play().get()

    assert player.Metadata['xesam:trackNumber'] == GLib.Variant('i', 7)


def test_get_volume_should_return_volume_between_zero_and_one(core, player):
    # dummy_mixer starts out with None as the volume
    assert player.Volume == 0

    core.mixer.set_volume(0)
    assert player.Volume == 0

    core.mixer.set_volume(50)
    assert player.Volume == 0.5

    core.mixer.set_volume(100)
    assert player.Volume == 1


def test_get_volume_should_return_0_if_muted(core, player):
    assert player.Volume == 0

    core.mixer.set_volume(100)
    assert player.Volume == 1

    core.mixer.set_mute(True)
    assert player.Volume == 0

    core.mixer.set_mute(False)
    assert player.Volume == 1


@pytest.mark.parametrize('volume, expected', [
    (-1.0, 0),
    (0, 0),
    (0.5, 50),
    (1.0, 100),
    (2.0, 100),
])
def test_set_volume(core, player, volume, expected):
    player.Volume = volume

    assert core.mixer.get_volume().get() == expected


def test_set_volume_to_not_a_number_does_not_change_volume(core, player):
    core.mixer.set_volume(10).get()

    player.Volume = None

    assert core.mixer.get_volume().get() == 10


def test_set_volume_is_ignored_if_can_control_is_false(core, player):
    player._CanControl = False
    core.mixer.set_volume(0)

    player.Volume = 1.0

    assert core.mixer.get_volume().get() == 0


def test_set_volume_to_positive_value_unmutes_if_muted(core, player):
    core.mixer.set_volume(10).get()
    core.mixer.set_mute(True).get()

    player.Volume = 1.0

    assert core.mixer.get_volume().get() == 100
    assert core.mixer.get_mute().get() is False


def test_set_volume_to_zero_does_not_unmute_if_muted(core, player):
    core.mixer.set_volume(10).get()
    core.mixer.set_mute(True).get()

    player.Volume = 0.0

    assert core.mixer.get_volume().get() == 0
    assert core.mixer.get_mute().get() is True


def test_get_position_returns_time_position_in_microseconds(core, player):
    core.tracklist.add([Track(uri='dummy:a', length=40000)])
    core.playback.play().get()
    core.playback.seek(10000).get()

    result_in_microseconds = player.Position

    result_in_milliseconds = result_in_microseconds // 1000
    assert result_in_milliseconds >= 10000


def test_get_position_when_no_current_track_should_be_zero(player):
    result_in_microseconds = player.Position

    result_in_milliseconds = result_in_microseconds // 1000
    assert result_in_milliseconds == 0


def test_get_minimum_rate_is_one_or_less(player):
    assert player.MinimumRate <= 1.0


def test_get_maximum_rate_is_one_or_more(player):
    assert player.MaximumRate >= 1.0


def test_can_go_next_is_true_if_can_control_and_other_next_track(core, player):
    player._CanControl = True
    core.tracklist.add([Track(uri='dummy:a'), Track(uri='dummy:b')])
    core.playback.play().get()

    assert player.CanGoNext


def test_can_go_next_is_false_if_next_track_is_the_same(core, player):
    player._CanControl = True
    core.tracklist.add([Track(uri='dummy:a')])
    core.tracklist.set_repeat(True)
    core.playback.play().get()

    assert not player.CanGoNext


def test_can_go_next_is_false_if_can_control_is_false(core, player):
    player._CanControl = False
    core.tracklist.add([Track(uri='dummy:a'), Track(uri='dummy:b')])
    core.playback.play().get()

    assert not player.CanGoNext


def test_can_go_previous_is_true_if_can_control_and_previous_track(
        core, player):
    player._CanControl = True
    core.tracklist.add([Track(uri='dummy:a'), Track(uri='dummy:b')])
    core.playback.play().get()
    core.playback.next().get()

    assert player.CanGoPrevious


def test_can_go_previous_is_false_if_previous_track_is_the_same(core, player):
    player._CanControl = True
    core.tracklist.add([Track(uri='dummy:a')])
    core.tracklist.set_repeat(True)
    core.playback.play().get()

    assert not player.CanGoPrevious


def test_can_go_previous_is_false_if_can_control_is_false(core, player):
    player._CanControl = False
    core.tracklist.add([Track(uri='dummy:a'), Track(uri='dummy:b')])
    core.playback.play().get()
    core.playback.next().get()

    assert not player.CanGoPrevious


def test_can_play_is_true_if_can_control_and_current_track(core, player):
    player._CanControl = True
    core.tracklist.add([Track(uri='dummy:a')])
    core.playback.play().get()
    assert core.playback.get_current_track().get()

    assert player.CanPlay


def test_can_play_is_false_if_no_current_track(core, player):
    player._CanControl = True
    assert not core.playback.get_current_track().get()

    assert not player.CanPlay


def test_can_play_if_false_if_can_control_is_false(core, player):
    player._CanControl = False

    assert not player.CanPlay


def test_can_pause_is_true_if_can_control_and_track_can_be_paused(
        core, player):
    player._CanControl = True

    assert player.CanPause


def test_can_pause_if_false_if_can_control_is_false(core, player):
    player._CanControl = False

    assert not player.CanPause


def test_can_seek_is_true_if_can_control_is_true(core, player):
    player._CanControl = True

    assert player.CanSeek


def test_can_seek_is_false_if_can_control_is_false(core, player):
    player._CanControl = False
    result = player.CanSeek
    assert not result


def test_can_control_is_true(core, player):
    result = player.CanControl
    assert result


def test_next_is_ignored_if_can_go_next_is_false(core, player):
    player._CanControl = False
    assert not player.CanGoNext
    core.tracklist.add([Track(uri='dummy:a'), Track(uri='dummy:b')])
    core.playback.play().get()
    assert core.playback.get_current_track().get().uri == 'dummy:a'

    player.Next()

    assert core.playback.get_current_track().get().uri == 'dummy:a'


def test_next_when_playing_skips_to_next_track_and_keep_playing(core, player):
    core.tracklist.add([Track(uri='dummy:a'), Track(uri='dummy:b')])
    core.playback.play().get()
    assert core.playback.get_current_track().get().uri == 'dummy:a'
    assert core.playback.get_state().get() == PLAYING

    player.Next()

    assert core.playback.get_current_track().get().uri == 'dummy:b'
    assert core.playback.get_state().get() == PLAYING


def test_next_when_at_end_of_list_should_stop_playback(core, player):
    core.tracklist.add([Track(uri='dummy:a'), Track(uri='dummy:b')])
    core.playback.play().get()
    core.playback.next().get()
    assert core.playback.get_current_track().get().uri == 'dummy:b'
    assert core.playback.get_state().get() == PLAYING
    player.Next()
    assert core.playback.get_state().get() == STOPPED


def test_next_when_paused_should_skip_to_next_track_and_stay_paused(
        core, player):
    core.tracklist.add([Track(uri='dummy:a'), Track(uri='dummy:b')])
    core.playback.play().get()
    core.playback.pause().get()
    assert core.playback.get_current_track().get().uri == 'dummy:a'
    assert core.playback.get_state().get() == PAUSED
    player.Next()
    assert core.playback.get_current_track().get().uri == 'dummy:b'
    assert core.playback.get_state().get() == PAUSED


def test_next_when_stopped_skips_to_next_track_and_stay_stopped(core, player):
    core.tracklist.add([Track(uri='dummy:a'), Track(uri='dummy:b')])
    core.playback.play().get()
    core.playback.stop()
    assert core.playback.get_current_track().get().uri == 'dummy:a'
    assert core.playback.get_state().get() == STOPPED
    player.Next()
    assert core.playback.get_current_track().get().uri == 'dummy:b'
    assert core.playback.get_state().get() == STOPPED


def test_previous_is_ignored_if_can_go_previous_is_false(core, player):
    player._CanControl = False
    assert not player.CanGoPrevious
    core.tracklist.add([Track(uri='dummy:a'), Track(uri='dummy:b')])
    core.playback.play().get()
    core.playback.next().get()
    assert core.playback.get_current_track().get().uri == 'dummy:b'

    player.Previous()

    assert core.playback.get_current_track().get().uri == 'dummy:b'


def test_previous_when_playing_skips_to_prev_track_and_keep_playing(
        core, player):
    core.tracklist.add([Track(uri='dummy:a'), Track(uri='dummy:b')])
    core.playback.play().get()
    core.playback.next().get()
    assert core.playback.get_current_track().get().uri == 'dummy:b'
    assert core.playback.get_state().get() == PLAYING

    player.Previous()

    assert core.playback.get_current_track().get().uri == 'dummy:a'
    assert core.playback.get_state().get() == PLAYING


def test_previous_when_at_start_of_list_should_stop_playback(core, player):
    core.tracklist.add([Track(uri='dummy:a'), Track(uri='dummy:b')])
    core.playback.play().get()
    assert core.playback.get_current_track().get().uri == 'dummy:a'
    assert core.playback.get_state().get() == PLAYING

    player.Previous()

    assert core.playback.get_state().get() == STOPPED


def test_previous_when_paused_skips_to_previous_track_and_pause(core, player):
    core.tracklist.add([Track(uri='dummy:a'), Track(uri='dummy:b')])
    core.playback.play().get()
    core.playback.next().get()
    core.playback.pause().get()
    assert core.playback.get_current_track().get().uri == 'dummy:b'
    assert core.playback.get_state().get() == PAUSED

    player.Previous()

    assert core.playback.get_current_track().get().uri == 'dummy:a'
    assert core.playback.get_state().get() == PAUSED


def test_previous_when_stopped_skips_to_previous_track_and_stops(core, player):
    core.tracklist.add([Track(uri='dummy:a'), Track(uri='dummy:b')])
    core.playback.play().get()
    core.playback.next().get()
    core.playback.stop()
    assert core.playback.get_current_track().get().uri == 'dummy:b'
    assert core.playback.get_state().get() == STOPPED

    player.Previous()

    assert core.playback.get_current_track().get().uri == 'dummy:a'
    assert core.playback.get_state().get() == STOPPED


def test_pause_is_ignored_if_can_pause_is_false(core, player):
    player._CanControl = False
    assert not player.CanPause
    core.tracklist.add([Track(uri='dummy:a'), Track(uri='dummy:b')])
    core.playback.play().get()
    assert core.playback.get_state().get() == PLAYING

    player.Pause()

    assert core.playback.get_state().get() == PLAYING


def test_pause_when_playing_should_pause_playback(core, player):
    core.tracklist.add([Track(uri='dummy:a'), Track(uri='dummy:b')])
    core.playback.play().get()
    assert core.playback.get_state().get() == PLAYING

    player.Pause()

    assert core.playback.get_state().get() == PAUSED


def test_pause_when_paused_has_no_effect(core, player):
    core.tracklist.add([Track(uri='dummy:a'), Track(uri='dummy:b')])
    core.playback.play().get()
    core.playback.pause().get()
    assert core.playback.get_state().get() == PAUSED

    player.Pause()

    assert core.playback.get_state().get() == PAUSED


def test_playpause_is_ignored_if_can_pause_is_false(core, player):
    player._CanControl = False
    assert not player.CanPause
    core.tracklist.add([Track(uri='dummy:a'), Track(uri='dummy:b')])
    core.playback.play().get()
    assert core.playback.get_state().get() == PLAYING

    player.PlayPause()

    assert core.playback.get_state().get() == PLAYING


def test_playpause_when_playing_should_pause_playback(core, player):
    core.tracklist.add([Track(uri='dummy:a'), Track(uri='dummy:b')])
    core.playback.play().get()
    assert core.playback.get_state().get() == PLAYING

    player.PlayPause()

    assert core.playback.get_state().get() == PAUSED


def test_playpause_when_paused_should_resume_playback(core, player):
    core.tracklist.add([Track(uri='dummy:a'), Track(uri='dummy:b')])
    core.playback.play().get()
    core.playback.pause().get()

    assert core.playback.get_state().get() == PAUSED
    at_pause = core.playback.get_time_position().get()
    assert at_pause >= 0

    player.PlayPause()

    assert core.playback.get_state().get() == PLAYING
    after_pause = core.playback.get_time_position().get()
    assert after_pause >= at_pause


def test_playpause_when_stopped_should_start_playback(core, player):
    core.tracklist.add([Track(uri='dummy:a'), Track(uri='dummy:b')])
    assert core.playback.get_state().get() == STOPPED

    player.PlayPause()

    assert core.playback.get_state().get() == PLAYING


def test_stop_is_ignored_if_can_control_is_false(core, player):
    player._CanControl = False
    core.tracklist.add([Track(uri='dummy:a'), Track(uri='dummy:b')])
    core.playback.play().get()
    assert core.playback.get_state().get() == PLAYING

    player.Stop()

    assert core.playback.get_state().get() == PLAYING


def test_stop_when_playing_should_stop_playback(core, player):
    core.tracklist.add([Track(uri='dummy:a'), Track(uri='dummy:b')])
    core.playback.play().get()
    assert core.playback.get_state().get() == PLAYING

    player.Stop()

    assert core.playback.get_state().get() == STOPPED


def test_stop_when_paused_should_stop_playback(core, player):
    core.tracklist.add([Track(uri='dummy:a'), Track(uri='dummy:b')])
    core.playback.play().get()
    core.playback.pause().get()
    assert core.playback.get_state().get() == PAUSED

    player.Stop()

    assert core.playback.get_state().get() == STOPPED


def test_play_is_ignored_if_can_play_is_false(core, player):
    player._CanControl = False
    assert not player.CanPlay
    core.tracklist.add([Track(uri='dummy:a'), Track(uri='dummy:b')])
    assert core.playback.get_state().get() == STOPPED

    player.Play()

    assert core.playback.get_state().get() == STOPPED


def test_play_when_stopped_starts_playback(core, player):
    core.tracklist.add([Track(uri='dummy:a'), Track(uri='dummy:b')])
    assert core.playback.get_state().get() == STOPPED

    player.Play()

    assert core.playback.get_state().get() == PLAYING


def test_play_after_pause_resumes_from_same_position(core, player):
    core.tracklist.add([Track(uri='dummy:a', length=40000)])
    core.playback.play().get()

    before_pause = core.playback.get_time_position().get()
    assert before_pause >= 0

    player.Pause()

    assert core.playback.get_state().get() == PAUSED
    at_pause = core.playback.get_time_position().get()
    assert at_pause >= before_pause

    player.Play()

    assert core.playback.get_state().get() == PLAYING
    after_pause = core.playback.get_time_position().get()
    assert after_pause >= at_pause


def test_play_when_there_is_no_track_has_no_effect(core, player):
    core.tracklist.clear()
    assert core.playback.get_state().get() == STOPPED

    player.Play()

    assert core.playback.get_state().get() == STOPPED


def test_seek_is_ignored_if_can_seek_is_false(core, player):
    player._CanControl = False
    assert not player.CanSeek
    core.tracklist.add([Track(uri='dummy:a', length=40000)])
    core.playback.play().get()

    before_seek = core.playback.get_time_position().get()
    assert before_seek >= 0

    milliseconds_to_seek = 10000
    microseconds_to_seek = milliseconds_to_seek * 1000

    player.Seek(microseconds_to_seek)

    after_seek = core.playback.get_time_position().get()
    assert before_seek <= after_seek
    assert after_seek < before_seek + milliseconds_to_seek


def test_seek_seeks_given_microseconds_forward_in_the_current_track(
        core, player):
    core.tracklist.add([Track(uri='dummy:a', length=40000)])
    core.playback.play().get()

    before_seek = core.playback.get_time_position().get()
    assert before_seek >= 0

    milliseconds_to_seek = 10000
    microseconds_to_seek = milliseconds_to_seek * 1000

    player.Seek(microseconds_to_seek)

    assert core.playback.get_state().get() == PLAYING

    after_seek = core.playback.get_time_position().get()
    assert after_seek >= before_seek + milliseconds_to_seek


def test_seek_seeks_given_microseconds_backward_if_negative(core, player):
    core.tracklist.add([Track(uri='dummy:a', length=40000)])
    core.playback.play().get()
    core.playback.seek(20000).get()

    before_seek = core.playback.get_time_position().get()
    assert before_seek >= 20000

    milliseconds_to_seek = -10000
    microseconds_to_seek = milliseconds_to_seek * 1000

    player.Seek(microseconds_to_seek)

    assert core.playback.get_state().get() == PLAYING

    after_seek = core.playback.get_time_position().get()
    assert after_seek >= before_seek + milliseconds_to_seek
    assert after_seek < before_seek


def test_seek_seeks_to_start_of_track_if_new_position_is_negative(
        core, player):
    core.tracklist.add([Track(uri='dummy:a', length=40000)])
    core.playback.play().get()
    core.playback.seek(20000).get()

    before_seek = core.playback.get_time_position().get()
    assert before_seek >= 20000

    milliseconds_to_seek = -30000
    microseconds_to_seek = milliseconds_to_seek * 1000

    player.Seek(microseconds_to_seek)

    assert core.playback.get_state().get() == PLAYING

    after_seek = core.playback.get_time_position().get()
    assert after_seek >= before_seek + milliseconds_to_seek
    assert after_seek < before_seek
    assert after_seek >= 0


def test_seek_skips_to_next_track_if_new_position_gt_track_length(
        core, player):
    core.tracklist.add([
        Track(uri='dummy:a', length=40000),
        Track(uri='dummy:b')])
    core.playback.play().get()
    core.playback.seek(20000).get()

    before_seek = core.playback.get_time_position().get()
    assert before_seek >= 20000
    assert core.playback.get_state().get() == PLAYING
    assert core.playback.get_current_track().get().uri == 'dummy:a'

    milliseconds_to_seek = 50000
    microseconds_to_seek = milliseconds_to_seek * 1000

    player.Seek(microseconds_to_seek)

    assert core.playback.get_state().get() == PLAYING
    assert core.playback.get_current_track().get().uri == 'dummy:b'

    after_seek = core.playback.get_time_position().get()
    assert after_seek >= 0
    assert after_seek < before_seek


def test_set_position_is_ignored_if_can_seek_is_false(core, player):
    player.get_CanSeek = lambda *_: False
    core.tracklist.add([Track(uri='dummy:a', length=40000)])
    core.playback.play().get()

    before_set_position = core.playback.get_time_position().get()
    assert before_set_position <= 5000

    track_id = 'a'

    position_to_set_in_millisec = 20000
    position_to_set_in_microsec = position_to_set_in_millisec * 1000

    player.SetPosition(track_id, position_to_set_in_microsec)

    after_set_position = core.playback.get_time_position().get()
    assert before_set_position <= after_set_position
    assert after_set_position < position_to_set_in_millisec


def test_set_position_sets_the_current_track_position_in_microsecs(
        core, player):
    core.tracklist.add([Track(uri='dummy:a', length=40000)])
    core.playback.play().get()

    before_set_position = core.playback.get_time_position().get()
    assert before_set_position <= 5000
    assert core.playback.get_state().get() == PLAYING

    track_id = '/com/mopidy/track/1'

    position_to_set_in_millisec = 20000
    position_to_set_in_microsec = position_to_set_in_millisec * 1000

    player.SetPosition(track_id, position_to_set_in_microsec)

    assert core.playback.get_state().get() == PLAYING

    after_set_position = core.playback.get_time_position().get()
    assert after_set_position >= position_to_set_in_millisec


def test_set_position_does_nothing_if_the_position_is_negative(core, player):
    core.tracklist.add([Track(uri='dummy:a', length=40000)])
    core.playback.play().get()
    core.playback.seek(20000)

    before_set_position = core.playback.get_time_position().get()
    assert before_set_position >= 20000
    assert before_set_position <= 25000
    assert core.playback.get_state().get() == PLAYING
    assert core.playback.get_current_track().get().uri == 'dummy:a'

    track_id = '/com/mopidy/track/1'

    position_to_set_in_millisec = -1000
    position_to_set_in_microsec = position_to_set_in_millisec * 1000

    player.SetPosition(track_id, position_to_set_in_microsec)

    after_set_position = core.playback.get_time_position().get()
    assert after_set_position >= before_set_position
    assert core.playback.get_state().get() == PLAYING
    assert core.playback.get_current_track().get().uri == 'dummy:a'


def test_set_position_does_nothing_if_position_is_gt_track_length(
        core, player):
    core.tracklist.add([Track(uri='dummy:a', length=40000)])
    core.playback.play().get()
    core.playback.seek(20000)

    before_set_position = core.playback.get_time_position().get()
    assert before_set_position >= 20000
    assert before_set_position <= 25000
    assert core.playback.get_state().get() == PLAYING
    assert core.playback.get_current_track().get().uri == 'dummy:a'

    track_id = 'a'

    position_to_set_in_millisec = 50000
    position_to_set_in_microsec = position_to_set_in_millisec * 1000

    player.SetPosition(track_id, position_to_set_in_microsec)

    after_set_position = core.playback.get_time_position().get()
    assert after_set_position >= before_set_position
    assert core.playback.get_state().get() == PLAYING
    assert core.playback.get_current_track().get().uri == 'dummy:a'


def test_set_position_is_noop_if_track_id_isnt_current_track(core, player):
    core.tracklist.add([Track(uri='dummy:a', length=40000)])
    core.playback.play().get()
    core.playback.seek(20000)

    before_set_position = core.playback.get_time_position().get()
    assert before_set_position >= 20000
    assert before_set_position <= 25000
    assert core.playback.get_state().get() == PLAYING
    assert core.playback.get_current_track().get().uri == 'dummy:a'

    track_id = 'b'

    position_to_set_in_millisec = 0
    position_to_set_in_microsec = position_to_set_in_millisec * 1000

    player.SetPosition(track_id, position_to_set_in_microsec)

    after_set_position = core.playback.get_time_position().get()
    assert after_set_position >= before_set_position
    assert core.playback.get_state().get() == PLAYING
    assert core.playback.get_current_track().get().uri == 'dummy:a'


def test_open_uri_is_ignored_if_can_control_is_false(backend, core, player):
    player._CanControl = False
    backend.library.dummy_library = [
        Track(uri='dummy:/test/uri')]

    player.OpenUri('dummy:/test/uri')

    assert core.tracklist.get_length().get() == 0


def test_open_uri_ignores_uris_with_unknown_uri_scheme(backend, core, player):
    assert core.get_uri_schemes().get() == ['dummy']
    backend.library.dummy_library = [Track(uri='notdummy:/test/uri')]

    player.OpenUri('notdummy:/test/uri')

    assert core.tracklist.get_length().get() == 0


def test_open_uri_adds_uri_to_tracklist(backend, core, player):
    backend.library.dummy_library = [Track(uri='dummy:/test/uri')]

    player.OpenUri('dummy:/test/uri')

    assert core.tracklist.get_length().get() == 1
    assert core.tracklist.get_tracks().get()[0].uri == 'dummy:/test/uri'


def test_open_uri_starts_playback_of_new_track_if_stopped(
        backend, core, player):
    backend.library.dummy_library = [Track(uri='dummy:/test/uri')]
    core.tracklist.add([Track(uri='dummy:a'), Track(uri='dummy:b')])
    assert core.playback.get_state().get() == STOPPED

    player.OpenUri('dummy:/test/uri')

    assert core.playback.get_state().get() == PLAYING
    assert core.playback.get_current_track().get().uri == 'dummy:/test/uri'


def test_open_uri_starts_playback_of_new_track_if_paused(
        backend, core, player):
    backend.library.dummy_library = [Track(uri='dummy:/test/uri')]
    core.tracklist.add([Track(uri='dummy:a'), Track(uri='dummy:b')])
    core.playback.play().get()
    core.playback.pause().get()
    assert core.playback.get_state().get() == PAUSED
    assert core.playback.get_current_track().get().uri == 'dummy:a'

    player.OpenUri('dummy:/test/uri')

    assert core.playback.get_state().get() == PLAYING
    assert core.playback.get_current_track().get().uri == 'dummy:/test/uri'


def test_open_uri_starts_playback_of_new_track_if_playing(
        backend, core, player):
    backend.library.dummy_library = [Track(uri='dummy:/test/uri')]
    core.tracklist.add([Track(uri='dummy:a'), Track(uri='dummy:b')])
    core.playback.play().get()
    assert core.playback.get_state().get() == PLAYING
    assert core.playback.get_current_track().get().uri == 'dummy:a'

    player.OpenUri('dummy:/test/uri')

    assert core.playback.get_state().get() == PLAYING
    assert core.playback.get_current_track().get().uri == 'dummy:/test/uri'
