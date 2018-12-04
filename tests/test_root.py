from __future__ import unicode_literals

import pytest

from mopidy_mpris.root import Root


@pytest.fixture
def root(config, core):
    return Root(config, core)


def test_fullscreen_returns_false(root):
    assert root.Fullscreen is False


def test_setting_fullscreen_fails(root):
    root.Fullscreen = True

    assert root.Fullscreen is False


def test_can_set_fullscreen_returns_false(root):
    assert root.CanSetFullscreen is False


def test_can_raise_returns_false(root):
    assert root.CanRaise is False


def test_raise_does_nothing(root):
    root.Raise()


def test_can_quit_returns_false(root):
    assert root.CanQuit is False


def test_quit_does_nothing(root):
    root.Quit()


def test_has_track_list_returns_false(root):
    assert root.HasTrackList is False


def test_identify_is_mopidy(root):
    assert root.Identity == 'Mopidy'


def test_desktop_entry_is_blank(root, config):
    assert root.DesktopEntry == ''


def test_supported_uri_schemes_includes_backend_uri_schemes(root):
    assert root.SupportedUriSchemes == ['dummy']


def test_supported_mime_types_has_hardcoded_entries(root):
    assert root.SupportedMimeTypes == [
        'audio/mpeg',
        'audio/x-ms-wma',
        'audio/x-ms-asf',
        'audio/x-flac',
        'audio/flac',
        'audio/l16;channels=2;rate=44100',
        'audio/l16;rate=44100;channels=2',
    ]
