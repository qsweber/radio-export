import logging
import json
import requests
import os
import time
import typing

logger = logging.getLogger(__name__)


class SpotifyClient(object):
    def __init__(self) -> None:
        self.BASE_URL = "https://api.spotify.com"
        self.session = self._new_request_session()
        self.user_id = self._get_user_id()

    def _request(self, url: str, retry_count: int = 0) -> requests.Response:
        if retry_count > 3:
            logger.warn("retried 3 times, so giving up")
            raise Exception("retried 3 times so giving up")

        r = self.session.get(url)

        if r.status_code == 429:
            retry_after = int(r.headers["Retry-After"])
            logger.info(
                "Spotify rate-limit hit, waiting {} seconds".format(str(retry_after))
            )
            time.sleep(retry_after)
            self._request(url, retry_count + 1)

        return r

    def _get_access_token(self) -> str:
        access_variables = {
            "refresh_token": os.environ["SPOTIFY_REFRESH_TOKEN"],
            "client_id": os.environ["SPOTIPY_CLIENT_ID"],
            "client_secret": os.environ["SPOTIPY_CLIENT_SECRET"],
            "grant_type": "refresh_token",
        }

        p = requests.post(
            "https://accounts.spotify.com/api/token", data=access_variables
        )

        return typing.cast(str, json.loads(p.text)["access_token"])

    def _new_request_session(self) -> requests.Session:
        access_token = self._get_access_token()

        headers = {
            "Authorization": "Bearer {}".format(access_token),
            "Content-Type": "application/json",
        }

        session = requests.Session()
        session.headers.update(headers)
        session.hooks["response"].append(raise_if_not_ok)

        return session

    def _get_user_id(self) -> str:
        r = self._request("{}/v1/me".format(self.BASE_URL))

        return typing.cast(str, json.loads(r.text)["id"])

    def create_playlist(self, playlist_name: str) -> str:
        r = self.session.post(
            "{}/v1/users/{}/playlists".format(self.BASE_URL, self.user_id),
            data=json.dumps({"name": playlist_name}),
        )

        return typing.cast(str, json.loads(r.text)["id"])

    def _get_playlist_id(self, playlist_name: str) -> str:
        r = self._request(
            "{}/v1/users/{}/playlists".format(self.BASE_URL, self.user_id)
        )

        playlists = json.loads(r.text)

        matches = [
            typing.cast(str, playlist_dict["id"])
            for playlist_dict in playlists["items"]
            if playlist_dict["name"] == playlist_name
        ]

        if len(matches) != 1:
            raise Exception("no playlist with that name")

        return matches[0]

    def _get_playlist_url(self, playlist_id: str) -> str:
        return "{}/v1/users/{}/playlists/{}/tracks".format(
            self.BASE_URL, self.user_id, playlist_id,
        )

    def get_song_uris(self, playlist_name: str) -> typing.Set[str]:
        playlist_id = self._get_playlist_id(playlist_name)
        url = self._get_playlist_url(playlist_id)

        uris = []
        while True:
            r = self._request(url)
            r_text = json.loads(r.text)
            uris += [item["track"]["uri"] for item in r_text["items"]]
            url = r_text.get("next")
            if not url:
                break

        return set(uris)

    def delete_songs_from_playlist(
        self, playlist_name: str, song_uris: typing.Set[str]
    ) -> None:
        playlist_id = self._get_playlist_id(playlist_name)
        url = self._get_playlist_url(playlist_id)
        for uri_chunk in _chunks(song_uris, 50):
            payload = json.dumps({"tracks": [{"uri": uri} for uri in uri_chunk]})
            self.session.delete(url, data=payload)

    def add_songs_to_playlist(
        self, playlist_name: str, song_uris: typing.Set[str]
    ) -> None:
        playlist_id = self._get_playlist_id(playlist_name)
        url = self._get_playlist_url(playlist_id)
        for uri_chunk in _chunks(song_uris, 50):
            payload = json.dumps({"uris": uri_chunk})
            self.session.post(url, data=payload)

    def find_spotify_uri(self, song_name: str, artist_name: str) -> str:
        query = "track:{}+artist:{}".format(song_name, artist_name,)

        payload = {"query": query, "type": "track", "limit": "1"}
        payload_str = "&".join("{}={}".format(k, v) for k, v in payload.items())

        r = self._request("{}/v1/search?{}".format(self.BASE_URL, payload_str))

        r_text = json.loads(r.text)

        return typing.cast(str, r_text["tracks"]["items"][0]["uri"])


def raise_if_not_ok(r, *args, **kwargs) -> None:  # type: ignore
    if not r.ok and r.status_code != 429:
        error_message = "error code {}, reason {}, text {}".format(
            r.status_code, r.reason, r.text,
        )

        raise Exception(error_message)


def _chunks(
    items: typing.Set[str], n: int
) -> typing.Generator[typing.List[str], None, None]:
    """
    Yield successive n-sized chunks from l.
    http://stackoverflow.com/questions/312443/
    """
    items_list = list(items)
    for i in range(0, len(items_list), n):
        yield items_list[i : i + n]
