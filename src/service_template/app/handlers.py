import logging

from raven import Client
from raven.transport.requests import RequestsHTTPTransport

from service_template.clients.sqs import SqsMessage
from service_template.service_context import service_context


sentry = Client(transport=RequestsHTTPTransport)
logger = logging.getLogger(__name__)


def sqsHandler(func):
    def wrapper(event: dict, context: dict):
        messages = service_context.clients.sqs.parse_sqs_messages(event)
        for message in messages:
            try:
                func(message)
            except Exception:
                service_context.clients.sqs.set_visibility_timeout_with_backoff(message)
                sentry.captureException()
                raise

    return wrapper


@sqsHandler
def example(message: SqsMessage) -> None:
    logger.info("hey! {}".format(message.message_id))
