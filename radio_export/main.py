import importlib
import json
import os
import requests


def _get_access_token():
    access_variables = {
        'refresh_token': os.environ['SPOTIFY_REFRESH_TOKEN'],
        'client_id': os.environ['SPOTIPY_CLIENT_ID'],
        'client_secret': os.environ['SPOTIPY_CLIENT_SECRET'],
        'grant_type': 'refresh_token',
    }

    p = requests.post(
        'https://accounts.spotify.com/api/token',
        data=access_variables
    )

    return json.loads(p.text)['access_token']


def _new_request_session():
    access_token = _get_access_token()

    headers = {
        'Authorization': 'Bearer {}'.format(access_token),
        'Content-Type': 'application/json',
    }

    session = requests.Session()
    session.headers.update(headers)
    session.hooks['response'].append(_raise_not_ok)

    return session


def _raise_not_ok(r, *args, **kwargs):
    if not r.ok:
        error_message = 'error code {}, reason {}, text {}'.format(
            r.status_code,
            r.reason,
            r.text,
        )

        raise Exception(error_message)


def _get_user_id(session):
    r = session.get('https://api.spotify.com/v1/me')

    return json.loads(r.text)['id']


def _get_spotify_track_from_song(session, song):
    query = 'track:{}+artist:{}'.format(song.song, song.artist)

    payload = {'query': query, 'type': 'track', 'limit': '1'}
    payload_str = '&'.join('{}={}'.format(k, v) for k, v in payload.items())

    r = requests.get(
        'https://api.spotify.com/v1/search?{}'.format(payload_str),
    )
    r_text = json.loads(r.text)

    try:
        return r_text['tracks']['items'][0]['uri']
    except:
        print(song)
        return ''


def _get_playlist_id_from_name(session, playlist_name, user_id):
    r = session.get(
        "https://api.spotify.com/v1/users/" + user_id + "/playlists",
    )
    playlists = json.loads(r.text)

    playlist_id = [
        playlist_dict['id']
        for playlist_dict in playlists['items']
        if playlist_dict['name'] == playlist_name
    ][0]

    return playlist_id


def _get_song_uris_in_playlist_id(session, playlist_id, user_id):
    r = session.get(
        "https://api.spotify.com/v1/users/" + user_id + "/playlists/" + playlist_id + "/tracks",
    )
    return [
        item['track']['uri']
        for item in json.loads(r.text)['items']
    ]


def _delete_songs_from_playlist(session, playlist_id, user_id, song_uris):
    url = "https://api.spotify.com/v1/users/" + user_id + "/playlists/" + playlist_id + "/tracks"
    for uri in song_uris:
        payload = json.dumps({"tracks": [{"uri": uri}]})
        session.delete(url, data=payload)


def _add_songs_to_playlist(session, playlist_id, user_id, song_uris):
    url = "https://api.spotify.com/v1/users/" + user_id + "/playlists/" + playlist_id + "/tracks"
    for uri in song_uris:
        if uri == '':
            continue
        payload = {'uris': uri}
        r = session.post(url, params=payload)


def _get_module(subpackage, module):
    module_name = 'radio_export.{subpackage}.{module}'.format(
        subpackage=subpackage,
        module=module,
    ).lower()

    return importlib.import_module(module_name)


def main(station, playlist_name):
    station_module = _get_module(
        subpackage='station',
        module=station,
    )

    songs = station_module.get_current_songs()

    session = _new_request_session()

    tracks = [
        _get_spotify_track_from_song(session, song)
        for song in songs
    ]

    user_id = _get_user_id(session)
    playlist_id = _get_playlist_id_from_name(session, playlist_name)

    current_uris = _get_song_uris_in_playlist_id(
        session,
        playlist_id,
        user_id,
    )

    to_add = set(tracks) - set(current_uris)
    to_delete = set(current_uris) - set(tracks)

    _delete_songs_from_playlist(session, playlist_id, user_id, to_delete)
    _add_songs_to_playlist(session, playlist_id, user_id, to_add)
