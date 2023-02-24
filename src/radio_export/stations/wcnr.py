from datetime import datetime
from typing import Any, List, Optional
import requests

from bs4 import BeautifulSoup

from radio_export.stations.base import Base, Song


class Wcnr(Base):
    playlist_name = "The Corner Live"

    def get_current_songs(self) -> List[Song]:
        response = requests.get(
            "http://1061thecorner.com/most-played/",
            headers={"User-Agent": "Mozilla/5.0"},
        )

        soup = BeautifulSoup(response.text, "html.parser")

        rows = soup.find("div", {"id": "page"}).find("table").find_all("tr")  # type: ignore
        rows.pop(0)

        songs = [self._get_song_from_row(row) for row in rows]

        return [song for song in songs if song]

    def _get_song_from_row(self, row: Any) -> Optional[Song]:
        td_with_text = [td.text for td in row.find_all("td") if td.text]

        if len(td_with_text) < 3:
            return None

        artist = td_with_text[1]

        song = td_with_text[2]

        return Song(
            played_at=datetime.now(),
            artist=artist,
            song=song,
        )
