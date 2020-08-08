import logging
import json
import typing

from jsonschema import validate  # type: ignore

from flask import Flask, jsonify, request, Response
from raven import Client  # type: ignore
from raven.contrib.flask import Sentry  # type: ignore
from raven.transport.requests import RequestsHTTPTransport  # type: ignore


app = Flask(__name__)
sentry = Sentry(app, client=Client(transport=RequestsHTTPTransport,),)
logger = logging.getLogger(__name__)


def schema(
    schema: typing.Any,
) -> typing.Callable[[typing.Callable[..., Response]], typing.Callable[..., Response]]:
    def wrapper(
        func: typing.Callable[..., Response],
    ) -> typing.Callable[..., Response]:
        def what_gets_called(*args: typing.Any, **kwargs: typing.Any) -> Response:
            if request.method == "GET":
                validate(instance=request.args, schema=schema)
            elif request.method == "POST":
                validate(instance=request.form, schema=schema)
            else:
                raise Exception("unexpected method {}".format(request.method))
            return func(*args, **kwargs)

        return what_gets_called

    return wrapper


@app.route("/api/v0/status", methods=["GET"])
def status() -> Response:
    logger.info("recieved request {}".format(json.dumps(request.json)))

    response = jsonify({"text": "ok"})
    response.headers.add("Access-Control-Allow-Origin", "*")

    return typing.cast(Response, response)


@app.route("/api/v0/foo", methods=["POST", "GET"])
@schema(
    {
        "type": "object",
        "properties": {"foo": {"type": "string"}, "bar": {"type": "string"}},
        "required": ["foo", "bar"],
    }
)
def status_typed() -> Response:
    data = request.form if request.method == "POST" else request.args
    response = jsonify(data)
    response.headers.add("Access-Control-Allow-Origin", "*")

    return typing.cast(Response, response)
