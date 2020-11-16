from typing import NamedTuple

from radio_export.clients.spotify import SpotifyClient
from radio_export.stations.wcnr import Wcnr
from radio_export.stations.wxpn import Wxpn
from radio_export.stations.kexp import Kexp


class Clients(NamedTuple):
    spotify: SpotifyClient


class Stations(NamedTuple):
    wcnr: Wcnr
    wxpn: Wxpn
    kexp: Kexp


class ServiceContext(NamedTuple):
    clients: Clients
    stations: Stations


service_context = ServiceContext(
    clients=Clients(
        spotify=SpotifyClient(),
    ),
    stations=Stations(wcnr=Wcnr(), wxpn=Wxpn(), kexp=Kexp()),
)
