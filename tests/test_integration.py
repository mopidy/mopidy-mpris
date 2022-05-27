from time import sleep
from unittest.mock import call

import pytest
from mopidy.models import Track

import mopidy_mpris

from . import DictFields


def player_call(can_play, can_go_next, can_go_previous):
    vals = DictFields(
        {
            "CanPlay": can_play,
            "CanGoNext": can_go_next,
            "CanGoPrevious": can_go_previous,
        }
    )
    return call("org.mpris.MediaPlayer2.Player", vals, [])


def assert_called(can_play, can_go_next, can_go_previous):
    # Beware the multithreading! Wait for the signal to get emitted.
    sleep(0.1)
    mopidy_mpris.interface.Interface.PropertiesChanged.assert_has_calls(
        [player_call(can_play, can_go_next, can_go_previous)]
    )
    mopidy_mpris.interface.Interface.PropertiesChanged.reset_mock()


def test_cold_start(frontend, core, player):
    assert not player.CanPlay
    assert not player.CanGoNext
    assert not player.CanGoPrevious
    core.tracklist.add([Track(uri="dummy:a"), Track(uri="dummy:b")]).get()
    assert_called(True, True, False)


def test_tracklist_full_to_empty(frontend, core, player):
    core.tracklist.add([Track(uri="dummy:a"), Track(uri="dummy:b")]).get()
    assert_called(True, True, False)
    core.tracklist.clear().get()
    assert_called(False, False, False)


def test_tracklist_changed_empty_while_playing(frontend, core, player):
    core.tracklist.add([Track(uri="dummy:a")]).get()
    assert_called(True, True, False)
    core.playback.play().get()
    assert_called(True, True, True)
    core.tracklist.clear().get()
    assert_called(False, False, False)


@pytest.mark.parametrize("frontend", ["fail"], indirect=True)
def test_frontend_fail_stops_actor(frontend):
    sleep(0.1)
    assert not frontend.actor_ref.is_alive()
