from datetime import datetime
import requests

from bs4 import BeautifulSoup

from radio_export.song import Song


def _get_song_from_row(row):
    td_with_text = [td.text for td in row.find_all('td') if td.text]

    artist = td_with_text[1]

    song = td_with_text[2]

    return Song(
        datetime=datetime.now(),
        artist=artist,
        song=song,
    )


def get_current_songs():
    url = 'http://1061thecorner.com/most-played/'

    foo = requests.get(
        url,
        headers={'User-Agent': 'Mozilla/5.0'},
    )

    soup = BeautifulSoup(foo.text, "html.parser")

    rows = soup.find('div', {'id': 'page'}).find('table').find_all('tr')
    rows.pop(0)

    return [
        _get_song_from_row(row)
        for row in rows
    ]
