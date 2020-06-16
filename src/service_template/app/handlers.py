import logging
import typing

from raven import Client  # type: ignore
from raven.transport.requests import RequestsHTTPTransport  # type: ignore

from service_template.clients.sqs import SqsMessage
from service_template.app.service_context import service_context


sentry = Client(transport=RequestsHTTPTransport)
logger = logging.getLogger(__name__)


def sqsHandler(
    func: typing.Callable[[SqsMessage], None]
) -> typing.Callable[[typing.Any], typing.Any]:
    def wrapper(event: typing.Dict[str, typing.Any]) -> None:
        messages = service_context.clients.sqs.parse_sqs_messages(event)
        for message in messages:
            try:
                func(message)
            except Exception:
                service_context.clients.sqs.set_visibility_timeout_with_backoff(message)
                sentry.captureException()
                raise

    return wrapper


def cronHandler(func: typing.Callable[[], None]) -> typing.Callable[[], None]:
    def wrapper() -> None:
        try:
            func()
        except Exception:
            sentry.captureException()
            raise

    return wrapper


@sqsHandler
def event_driven_task(message: SqsMessage) -> None:
    logger.info("hey! {}".format(message.message_id))


@cronHandler
def time_driven_task() -> None:
    logger.info("it's time!")
