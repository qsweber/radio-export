import argparse
import importlib
import json
import os
import time
import requests

BASE_URL = 'https://api.spotify.com'


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
    r = session.get('{}/v1/me'.format(BASE_URL))

    return json.loads(r.text)['id']


def _get_spotify_track_from_song(session, song):
    time.sleep(1)
    query = 'track:{}+artist:{}'.format(
        song.song,
        song.artist,
    )

    payload = {'query': query, 'type': 'track', 'limit': '1'}
    payload_str = '&'.join('{}={}'.format(k, v) for k, v in payload.items())

    r = session.get(
        '{}/v1/search?{}'.format(BASE_URL, payload_str),
    )
    r_text = json.loads(r.text)

    try:
        return r_text['tracks']['items'][0]['uri']
    except:
        return None


def _create_playlist(session, playlist_name, user_id):
    r = session.post(
        '{}/v1/users/{}/playlists'.format(BASE_URL, user_id),
        data=json.dumps({'name': playlist_name})
    )

    return json.loads(r.text)['id']


def _get_playlist_id_from_name(session, playlist_name, user_id):
    r = session.get(
        '{}/v1/users/{}/playlists'.format(BASE_URL, user_id)
    )
    playlists = json.loads(r.text)

    matches = [
        playlist_dict['id']
        for playlist_dict in playlists['items']
        if playlist_dict['name'] == playlist_name
    ]

    if matches:
        playlist_id = matches[0]
    else:
        playlist_id = _create_playlist(session, playlist_name, user_id)

    return playlist_id


def _get_playlist_url(playlist_id, user_id):
    return '{}/v1/users/{}/playlists/{}/tracks'.format(
        BASE_URL,
        user_id,
        playlist_id,
    )


def _get_song_uris_in_playlist_id(session, playlist_id, user_id):
    url = _get_playlist_url(playlist_id, user_id)
    uris = []
    while True:
        r = session.get(url)
        r_text = json.loads(r.text)
        uris += [
            item['track']['uri']
            for item in r_text['items']
        ]
        url = r_text.get('next')
        if not url:
            break

    return set(uris)


def _chunks(l, n):
    '''
    Yield successive n-sized chunks from l.
    http://stackoverflow.com/questions/312443/
    '''
    l = list(l)
    for i in range(0, len(l), n):
        yield l[i:i + n]


def _delete_songs_from_playlist(session, playlist_id, user_id, song_uris):
    url = _get_playlist_url(playlist_id, user_id)
    for uri_chunk in _chunks(song_uris, 50):
        payload = json.dumps({"tracks": [{"uri": uri} for uri in uri_chunk]})
        session.delete(url, data=payload)


def _add_songs_to_playlist(session, playlist_id, user_id, song_uris):
    url = _get_playlist_url(playlist_id, user_id)
    for uri_chunk in _chunks(song_uris, 50):
        payload = json.dumps({'uris': uri_chunk})
        session.post(url, data=payload)


def _get_module(subpackage, module):
    module_name = 'radio_export.{subpackage}.{module}'.format(
        subpackage=subpackage,
        module=module,
    ).lower()

    return importlib.import_module(module_name)


def run(station, playlist_name):
    station_module = _get_module(
        subpackage='stations',
        module=station,
    )

    songs = station_module.get_current_songs()

    session = _new_request_session()

    tracks = [
        _get_spotify_track_from_song(session, song)
        for song in songs
    ]

    tracks = set([track for track in tracks if track])

    user_id = _get_user_id(session)
    playlist_id = _get_playlist_id_from_name(session, playlist_name, user_id)

    current_uris = _get_song_uris_in_playlist_id(
        session,
        playlist_id,
        user_id,
    )

    # to_delete = current_uris - tracks
    # to_add = tracks - current_uris

    # if to_delete:
    _delete_songs_from_playlist(session, playlist_id, user_id, current_uris)

    # if to_add:
    _add_songs_to_playlist(session, playlist_id, user_id, tracks)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--station', required=True)
    parser.add_argument('--playlist-name', required=True)

    cli_args = parser.parse_args()

    run(cli_args.station, cli_args.playlist_name)
