import requests


class BaseStation(object):
    def __init__(self, url, playlist_name):
        self.url = url
        self.playlist_name = playlist_name

    def scrape(self):
        return requests.get(
            self.url,
            headers={'User-Agent': 'Mozilla/5.0'},
        )

    def get_current_songs(self):
        raise Exception('not implemented')
