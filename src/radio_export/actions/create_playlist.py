import logging
import typing

from radio_export.app.service_context import ServiceContext
from radio_export.clients.spotify import SpotifyClient
from radio_export.stations.base import Base as Station, Song

logger = logging.getLogger(__name__)


def create_playlist(station: Station, service_context: ServiceContext) -> None:
    songs = station.get_current_songs()

    new_uris: typing.Set[str] = set()
    for song in songs:
        uri = _find_spotify_song(song, service_context.clients.spotify)
        if uri:
            new_uris.add(uri)

    current_uris = service_context.clients.spotify.get_song_uris(station.playlist_name)

    service_context.clients.spotify.delete_songs_from_playlist(
        station.playlist_name, current_uris,
    )

    service_context.clients.spotify.add_songs_to_playlist(
        station.playlist_name, new_uris,
    )


def _find_spotify_song(
    song: Song, spotify_client: SpotifyClient
) -> typing.Optional[str]:
    try:
        spotify_song = spotify_client.find_spotify_uri(song.song, song.artist,)

        logger.info(
            "found match for input song: {}, {}".format(song.song, song.artist,)
        )

        return spotify_song
    except Exception:
        logger.info("no match for input song: {}, {}".format(song.song, song.artist,))

        return None
