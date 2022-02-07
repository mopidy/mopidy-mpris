from unittest.mock import Mock, PropertyMock

import pytest
from mopidy.core import Core

from mopidy_mpris.frontend import MprisFrontend
from mopidy_mpris.player import Player
from mopidy_mpris.playlists import Playlists
from mopidy_mpris.root import Root
from mopidy_mpris.server import Server

from tests import dummy_audio, dummy_backend, dummy_mixer


@pytest.fixture
def config():
    return {
        "core": {"max_tracklist_length": 10000},
        "mpris": {"bus_type": "session"},
    }


@pytest.fixture
def audio():
    actor = dummy_audio.create_proxy()
    yield actor
    actor.stop()


@pytest.fixture
def backend(audio):
    actor = dummy_backend.create_proxy(audio=audio)
    yield actor
    actor.stop()


@pytest.fixture
def mixer():
    actor = dummy_mixer.create_proxy()
    yield actor
    actor.stop()


@pytest.fixture
def core(config, backend, mixer, audio):
    actor = Core.start(
        config=config, backends=[backend], mixer=mixer, audio=audio
    ).proxy()
    yield actor
    actor.stop()


@pytest.fixture
def root(config, core):
    return Root(config, core)


@pytest.fixture
def player(config, core):
    return Player(config, core)


@pytest.fixture
def playlists(config, core):
    return Playlists(config, core)


@pytest.fixture
def server(monkeypatch, config, core, player, root, playlists):
    with monkeypatch.context() as m:
        m.setattr("mopidy_mpris.server.Player", lambda *_: player)
        m.setattr("mopidy_mpris.server.Root", lambda *_: root)
        m.setattr("mopidy_mpris.server.Playlists", lambda *_: playlists)
        return Server(config, core)


@pytest.fixture
def frontend(request, monkeypatch, config, core, server):
    monkeypatch.setattr("mopidy_mpris.frontend.Server.publish", Mock())
    monkeypatch.setattr("mopidy_mpris.frontend.Server.unpublish", Mock())
    monkeypatch.setattr(
        "mopidy_mpris.interface.Interface.PropertiesChanged", PropertyMock()
    )
    server_dep = (
        Mock(side_effect=Exception)
        if getattr(request, "param", None) == "fail"
        else lambda *_: server
    )
    with monkeypatch.context() as m:
        m.setattr("mopidy_mpris.frontend.Server", server_dep)
        frontend = MprisFrontend.start(config, core).proxy()
    yield frontend
    frontend.stop()
