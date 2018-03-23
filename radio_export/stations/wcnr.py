from datetime import datetime

from bs4 import BeautifulSoup

from radio_export.stations.base import BaseStation
from radio_export.models.song import Song


class Wcnr(BaseStation):
    def __init__(self):
        super(Wcnr, self).__init__(
            'http://1061thecorner.com/most-played/',
            'The Corner Live',
        )

    def get_current_songs(self):
        response = self.scrape()

        soup = BeautifulSoup(response.text, "html.parser")

        rows = soup.find('div', {'id': 'page'}).find('table').find_all('tr')
        rows.pop(0)

        songs = [
            self.get_song_from_row(row)
            for row in rows
        ]

        return [song for song in songs if song]

    def get_song_from_row(self, row):
        td_with_text = [td.text for td in row.find_all('td') if td.text]

        if (len(td_with_text) < 3):
            return None

        artist = td_with_text[1]

        song = td_with_text[2]

        return Song(
            datetime=datetime.now(),
            artist=artist,
            song=song,
        )
