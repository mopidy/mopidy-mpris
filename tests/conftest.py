from __future__ import annotations

from typing import TYPE_CHECKING, cast

import pytest
from mopidy.core import Core

from tests import dummy_audio, dummy_backend, dummy_mixer

if TYPE_CHECKING:
    from collections.abc import Generator

    from mopidy.audio import AudioProxy
    from mopidy.backend import BackendProxy
    from mopidy.core import CoreProxy
    from mopidy.mixer import MixerProxy
    from mopidy.models import TlTrack, Track

    from tests import AddToTracklist


@pytest.fixture
def config():
    return {
        "core": {"max_tracklist_length": 10000},
    }


@pytest.fixture
def audio() -> Generator[AudioProxy]:
    actor = cast("AudioProxy", dummy_audio.create_proxy())
    yield actor
    actor.stop()


@pytest.fixture
def backend(audio) -> Generator[BackendProxy]:
    actor = cast("BackendProxy", dummy_backend.create_proxy(audio=audio))
    yield actor
    actor.stop()


@pytest.fixture
def mixer() -> Generator[MixerProxy]:
    actor = cast("MixerProxy", dummy_mixer.create_proxy())
    yield actor
    actor.stop()


@pytest.fixture
def core(config, backend, mixer, audio) -> Generator[CoreProxy]:
    actor = cast(
        "CoreProxy",
        Core.start(
            config=config,
            backends=[backend],
            mixer=mixer,
            audio=audio,
        ).proxy(),
    )
    yield actor
    actor.stop()


@pytest.fixture
def add_to_tracklist(backend: BackendProxy, core: CoreProxy) -> AddToTracklist:
    """Put tracks in the dummy library, and add them to the tracklist by URI."""

    def add(*tracks: Track) -> list[TlTrack]:
        uris = [track.uri for track in tracks]
        library = backend.library.dummy_library.get()
        backend.library.dummy_library = [
            *[track for track in library if track.uri not in uris],
            *tracks,
        ]
        return core.tracklist.add(uris=uris).get()

    return add
