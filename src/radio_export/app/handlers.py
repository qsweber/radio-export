import logging
import typing

from raven import Client  # type: ignore
from raven.transport.requests import RequestsHTTPTransport  # type: ignore

from radio_export.actions.create_playlist import (
    create_playlist as create_playlist_action,
)
from radio_export.app.service_context import service_context

sentry = Client(transport=RequestsHTTPTransport)
logger = logging.getLogger(__name__)


def cronHandler(func: typing.Callable[[], None]) -> typing.Callable[[], None]:
    def wrapper() -> None:
        try:
            func()
        except Exception:
            sentry.captureException()
            raise

    return wrapper


@cronHandler
def create_xpn_playlist() -> None:
    create_playlist_action(service_context.stations.wxpn, service_context)


@cronHandler
def create_wcnr_playlist() -> None:
    create_playlist_action(service_context.stations.wcnr, service_context)


@cronHandler
def create_kexp_playlist() -> None:
    create_playlist_action(service_context.stations.kexp, service_context)
