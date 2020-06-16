from functools import partial
import logging


logger = logging.getLogger(__name__)


def create_playlist(station, spotify_client):
    songs = station.get_current_songs()

    func = partial(
        _find_spotify_song,
        spotify_client=spotify_client
    )

    new_uris = list(filter(lambda s: s, map(func, songs)))

    current_uris = spotify_client.get_song_uris(station.playlist_name)

    spotify_client.delete_songs_from_playlist(
        station.playlist_name,
        current_uris,
    )

    spotify_client.add_songs_to_playlist(
        station.playlist_name,
        new_uris,
    )


def _find_spotify_song(song, spotify_client):
    try:
        spotify_song = spotify_client.find_spotify_uri(
            song.song,
            song.artist,
        )

        logger.info('found match for input song: {}, {}'.format(
            song.song,
            song.artist,
        ))

        return spotify_song
    except:
        logger.info('no match for input song: {}, {}'.format(
            song.song,
            song.artist,
        ))

        return None
