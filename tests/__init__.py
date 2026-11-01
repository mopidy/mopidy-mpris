from typing import Protocol

from mopidy.models import TlTrack, Track


class AddToTracklist(Protocol):
    def __call__(self, *tracks: Track) -> list[TlTrack]: ...
