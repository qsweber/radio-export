import logging

from flask import Flask, jsonify

from radio_export.actions.create_playlist import create_playlist as create_playlist_action
from radio_export.clients.spotify import SpotifyClient
from radio_export.stations.xpn import Xpn
from radio_export.stations.wcnr import Wcnr


app = Flask(__name__)
logger = logging.getLogger(__name__)


@app.route('/api/v0/status', methods=['GET'])
def status_http():
    '''
    Create a poll
    This is connected to an incoming slash command from Slack
    '''
    outgoing_message = {'ok': True}

    response = jsonify(outgoing_message)
    response.headers.add('Access-Control-Allow-Origin', '*')

    return response


def create_xpn_playlist():
    xpn = Xpn()
    spotify_client = SpotifyClient()

    create_playlist_action(xpn, spotify_client)


def create_wcnr_playlist():
    wcnr = Wcnr()
    spotify_client = SpotifyClient()

    create_playlist_action(wcnr, spotify_client)
