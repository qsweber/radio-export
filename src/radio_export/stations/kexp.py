from datetime import datetime
import json
from typing import List
import requests
from time import sleep

from radio_export.stations.base import Base, Song


class Kexp(Base):
    playlist_name = "KEXP Live"

    def get_current_songs(self) -> List[Song]:
        songs: List[Song] = []
        offset = 20
        while len(songs) == 0 or (
            len(songs) < 400
            and (
                max(songs, key=lambda a: a.played_at).played_at
                - min(songs, key=lambda a: a.played_at).played_at
            ).total_seconds()
            < (60 * 60 * 24)
        ):
            response = requests.get(
                "https://api.kexp.org/v2/plays",
                params={"limit": "20", "ordering": "-airdate", "offset": str(offset)},
                headers={"User-Agent": "Mozilla/5.0"},
            )

            parsed = json.loads(response.text)

            songs += [
                Song(
                    artist=row["artist"],
                    song=row["song"],
                    played_at=datetime.fromisoformat(row["airdate"]),
                )
                for row in parsed["results"]
                if "artist" in row and "song" in row and "airdate" in row
            ]

            offset += 20

            sleep(1)  # avoid spamming their servers

        return songs
