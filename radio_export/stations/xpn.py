from datetime import datetime
import logging
import requests

from bs4 import BeautifulSoup

from radio_export.song import Song


logger = logging.getLogger(__name__)


def _get_song_from_row(row, title):
    time = row[0:8]
    rest = row[8:]
    parts = rest.split(' - ')
    if len(parts) == 2:
        artist = parts[0].strip()
        song = parts[1].strip()
    else:
        logger.warning('Could not parse: {}'.format(row))

        return None

    return Song(
        datetime=datetime.strptime(
            '{} {}'.format(title, time),
            'XPN Playlist for %m-%d-%Y %H:%M %p'
        ),
        artist=artist,
        song=song,
    )


def get_current_songs():
    url = 'http://edge2.xpn.org/playlists/xpn-playlist'

    foo = requests.get(
        url,
        headers={'User-Agent': 'Mozilla/5.0'},
    )

    soup = BeautifulSoup(foo.text, "html.parser")
    body = soup.find('div', {'itemprop': 'articleBody'})

    title = body.find(
        'div',
        {'class': 'page-header'}
    ).find_next('h2').text.strip()

    rows = [
        row.text
        for row in body.find(
            'div',
            {'class': 'ui-widget-content'}
        ).find(
            'div',
            {'id': 'accordion'}
        ).findAll('h3')
        if not row.text.startswith('Like what you\'re hearing?') and
        'World Cafe' not in row.text and
        '|Echoes|' not in row.text
    ]

    songs = [
        _get_song_from_row(row, title)
        for row in rows
    ]

    return [song for song in songs if song]
