import logging
from typing import override

import pykka
from mopidy.config import Config
from mopidy.core import CoreEvent, CoreEventData, CoreListener, CoreProxy
from mopidy.models import Playlist, TlTrack
from mopidy.types import DurationMs, Percentage, PlaybackState, Uri

from mopidy_mpris.interface import Interface
from mopidy_mpris.playlists import get_playlist_id
from mopidy_mpris.server import Server

logger = logging.getLogger(__name__)


class MprisFrontend(pykka.ThreadingActor, CoreListener):
    @override
    def __init__(self, config: Config, core: CoreProxy) -> None:
        super().__init__()
        self.config = config
        self.core = core
        self.mpris: Server | None = None

    @override
    def on_start(self) -> None:
        try:
            self.mpris = Server(self.config, self.core)
            self.mpris.publish()
        except Exception as e:  # noqa: BLE001
            logger.warning("MPRIS frontend setup failed (%s)", e)
            self.stop()

    @override
    def on_stop(self) -> None:
        logger.debug("Removing MPRIS object from D-Bus connection...")
        if self.mpris:
            self.mpris.unpublish()
            self.mpris = None
        logger.debug("Removed MPRIS object from D-Bus connection")

    @override
    def on_event(self, event: CoreEvent, **kwargs: CoreEventData) -> None:
        logger.debug("Received %s event", event)
        if self.mpris is None:
            return None
        return super().on_event(event, **kwargs)

    @override
    def track_playback_paused(
        self,
        tl_track: TlTrack,
        time_position: DurationMs,
    ) -> None:
        assert self.mpris
        _emit_properties_changed(self.mpris.player, ["PlaybackStatus"])

    @override
    def track_playback_resumed(
        self,
        tl_track: TlTrack,
        time_position: DurationMs,
    ) -> None:
        assert self.mpris
        _emit_properties_changed(self.mpris.player, ["PlaybackStatus"])

    @override
    def track_playback_started(self, tl_track: TlTrack) -> None:
        assert self.mpris
        _emit_properties_changed(self.mpris.player, ["PlaybackStatus", "Metadata"])

    @override
    def track_playback_ended(
        self,
        tl_track: TlTrack,
        time_position: DurationMs,
    ) -> None:
        assert self.mpris
        _emit_properties_changed(self.mpris.player, ["PlaybackStatus", "Metadata"])

    @override
    def playback_state_changed(
        self,
        old_state: PlaybackState,
        new_state: PlaybackState,
    ) -> None:
        assert self.mpris
        _emit_properties_changed(self.mpris.player, ["PlaybackStatus", "Metadata"])

    @override
    def tracklist_changed(self) -> None:
        pass  # TODO: Implement if adding tracklist support

    @override
    def playlists_loaded(self) -> None:
        assert self.mpris
        _emit_properties_changed(self.mpris.playlists, ["PlaylistCount"])

    @override
    def playlist_changed(self, playlist: Playlist) -> None:
        assert self.mpris
        if playlist.uri is None:
            return
        playlist_id = get_playlist_id(playlist.uri)
        self.mpris.playlists.PlaylistChanged(playlist_id, playlist.name, "")  # pyright: ignore[reportCallIssue]

    @override
    def playlist_deleted(self, uri: Uri) -> None:
        assert self.mpris
        _emit_properties_changed(self.mpris.playlists, ["PlaylistCount"])

    @override
    def options_changed(self) -> None:
        assert self.mpris
        _emit_properties_changed(
            self.mpris.player,
            ["LoopStatus", "Shuffle", "CanGoPrevious", "CanGoNext"],
        )

    @override
    def volume_changed(self, volume: Percentage) -> None:
        assert self.mpris
        _emit_properties_changed(self.mpris.player, ["Volume"])

    @override
    def mute_changed(self, mute: bool) -> None:
        assert self.mpris
        _emit_properties_changed(self.mpris.player, ["Volume"])

    @override
    def seeked(self, time_position: DurationMs) -> None:
        assert self.mpris
        time_position_in_microseconds = time_position * 1000
        self.mpris.player.Seeked(time_position_in_microseconds)  # pyright: ignore[reportCallIssue]

    @override
    def stream_title_changed(self, title: str) -> None:
        assert self.mpris
        _emit_properties_changed(self.mpris.player, ["Metadata"])


def _emit_properties_changed(
    interface: Interface, changed_properties: list[str]
) -> None:
    props_with_new_values = [(p, getattr(interface, p)) for p in changed_properties]
    interface.PropertiesChanged(  # pyright: ignore[reportCallIssue]
        interface.INTERFACE,
        dict(props_with_new_values),
        [],
    )
