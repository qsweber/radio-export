from datetime import datetime, timedelta
from typing import List
import requests
import logging


from radio_export.stations.base import Base, Song

logger = logging.getLogger(__name__)


class Wxpn(Base):
    playlist_name = "XPN Live"

    def get_current_songs(self) -> List[Song]:
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        response = requests.get(
            "https://origin.xpn.org/utils/playlist/json/{}.json".format(yesterday),
            headers={"User-Agent": "Mozilla/5.0"},
        )

        return [
            Song(
                played_at=datetime.fromisoformat(raw["timeslice"]),
                artist=raw["artist"],
                song=raw["song"],
            )
            for raw in response.json()
            if raw["artist"] != "|World Cafe|"
            and raw["artist"] != "|Echoes|"
            and raw["artist"] != "|Rhythm Lab Radio|"
        ]
