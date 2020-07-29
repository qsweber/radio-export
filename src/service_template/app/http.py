import logging
import json

import typing

from flask import Flask, jsonify, request, Response, Request
from raven import Client  # type: ignore
from raven.contrib.flask import Sentry  # type: ignore
from raven.transport.requests import RequestsHTTPTransport  # type: ignore


app = Flask(__name__)
sentry = Sentry(app, client=Client(transport=RequestsHTTPTransport,),)
logger = logging.getLogger(__name__)


def f1(
    foo: str,
) -> typing.Callable[[typing.Callable[[int], float]], typing.Callable[[], float]]:
    def f2(func: typing.Callable[[int], float]) -> typing.Callable[[], float]:
        def what_gets_called() -> float:
            return func(123)

        return what_gets_called

    return f2


@app.route("/api/v0/status", methods=["GET"])
def status() -> Response:
    logger.info("recieved request with args {}".format(json.dumps(request.args)))

    response = jsonify({"text": "ok"})
    response.headers.add("Access-Control-Allow-Origin", "*")

    return typing.cast(Response, response)


@f1("hi")
def foo(baz: int) -> float:
    return baz + 0.1


T = typing.TypeVar("T")


def typedRoute(
    converter: typing.Callable[[Request], T], request2: Request
) -> typing.Callable[[typing.Callable[[T], Response]], typing.Callable[[], Response]]:
    foo = converter(request2)

    def wrapper(func: typing.Callable[[T], Response]) -> typing.Callable[[], Response]:
        def what_gets_called() -> Response:
            return func(foo)

        return what_gets_called

    return wrapper


class Foo(typing.NamedTuple):
    bar: str


def fooConverter(r: Request) -> Foo:
    return Foo(bar=r.args["abc"])


@app.route("/api/v0/presign", methods=["GET"])
@typedRoute(fooConverter, request)
def presign(foo: Foo) -> Response:
    response = jsonify({"text": foo.bar})
    response.headers.add("Access-Control-Allow-Origin", "*")

    return typing.cast(Response, response)
