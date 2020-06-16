from typing import NamedTuple

from radio_export.clients.spotify import SpotifyClient
from radio_export.stations.wcnr import Wcnr
from radio_export.stations.wxpn import Wxpn


class Clients(NamedTuple):
    spotify: SpotifyClient


class Stations(NamedTuple):
    wcnr: Wcnr
    wxpn: Wxpn


class ServiceContext(NamedTuple):
    clients: Clients
    stations: Stations


service_context = ServiceContext(
    clients=Clients(spotify=SpotifyClient(),),
    stations=Stations(wcnr=Wcnr(), wxpn=Wxpn()),
)
