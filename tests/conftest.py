from mopidy.core import Core

import pytest

from tests import dummy_audio, dummy_backend, dummy_mixer


@pytest.fixture
def config():
    return {
        'core': {
            'max_tracklist_length': 10000,
        },
        'mpris': {
            'desktop_file': '/tmp/mopidy.desktop',
        },
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
def core(config, backend, mixer):
    actor = Core.start(config=config, backends=[backend], mixer=mixer).proxy()
    yield actor
    actor.stop()
