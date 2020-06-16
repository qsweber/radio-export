from datetime import datetime
from typing import NamedTuple, List


class Song(NamedTuple):
    artist: str
    song: str
    played_at: datetime


class Base:
    playlist_name: str = "abstract"

    def get_current_songs(self) -> List[Song]:
        return []
