from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from mopidy_mpris.root import Root

if TYPE_CHECKING:
    from mopidy.config import Config
    from mopidy.core import CoreProxy


@pytest.fixture
def root(config: Config, core: CoreProxy) -> Root:
    return Root(config, core)


def test_fullscreen_returns_false(root: Root):
    assert root.Fullscreen is False


def test_setting_fullscreen_fails(root: Root):
    root.Fullscreen = True

    assert root.Fullscreen is False


def test_can_set_fullscreen_returns_false(root: Root):
    assert root.CanSetFullscreen is False


def test_can_raise_returns_false(root: Root):
    assert root.CanRaise is False


def test_raise_does_nothing(root: Root):
    root.Raise()


def test_can_quit_returns_false(root: Root):
    assert root.CanQuit is False


def test_quit_does_nothing(root: Root):
    root.Quit()


def test_has_track_list_returns_false(root: Root):
    assert root.HasTrackList is False


def test_identify_is_mopidy(root: Root):
    assert root.Identity == "Mopidy"


def test_desktop_entry_is_blank(root, config):
    assert root.DesktopEntry == ""


def test_supported_uri_schemes_includes_backend_uri_schemes(root: Root):
    assert root.SupportedUriSchemes == ["dummy"]


def test_supported_mime_types_has_hardcoded_entries(root: Root):
    assert root.SupportedMimeTypes == [
        "audio/mpeg",
        "audio/x-ms-wma",
        "audio/x-ms-asf",
        "audio/x-flac",
        "audio/flac",
        "audio/l16;channels=2;rate=44100",
        "audio/l16;rate=44100;channels=2",
    ]
