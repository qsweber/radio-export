from datetime import datetime
from typing import List, Optional
import requests
import logging

from bs4 import BeautifulSoup  # type: ignore

from radio_export.stations.base import Base, Song

logger = logging.getLogger(__name__)


class Wxpn(Base):
    playlist_name = "XPN Live"

    def get_current_songs(self) -> List[Song]:
        response = requests.get(
            "http://edge2.xpn.org/playlists/xpn-playlist",
            headers={"User-Agent": "Mozilla/5.0"},
        )

        soup = BeautifulSoup(response.text, "html.parser")
        body = soup.find("div", {"itemprop": "articleBody"})

        title = body.find("div", {"class": "page-header"}).find_next("h2").text.strip()

        rows = [
            row.text
            for row in body.find("div", {"class": "ui-widget-content"})
            .find("div", {"id": "accordion"})
            .findAll("h3")
            if not row.text.startswith("Like what you're hearing?")
            and "World Cafe" not in row.text
            and "|Echoes|" not in row.text
        ]

        songs = [self._get_song_from_row(row, title) for row in rows]

        return [song for song in songs if song]

    def _get_song_from_row(self, row: str, title: str) -> Optional[Song]:
        time = row[0:8]
        rest = row[8:]
        parts = rest.split(" - ")
        if len(parts) == 2:
            artist = parts[0].strip()
            song = parts[1].strip()
        else:
            logger.warning("Could not parse: {}".format(row))

            return None

        return Song(
            played_at=datetime.strptime(
                "{} {}".format(title, time), "XPN Playlist for %m-%d-%Y %H:%M %p"
            ),
            artist=artist,
            song=song,
        )
