import logging
import json

import typing

from flask import Flask, jsonify, request, Response
from raven import Client  # type: ignore
from raven.contrib.flask import Sentry  # type: ignore
from raven.transport.requests import RequestsHTTPTransport  # type: ignore


app = Flask(__name__)
sentry = Sentry(app, client=Client(transport=RequestsHTTPTransport,),)
logger = logging.getLogger(__name__)


@app.route("/api/v0/status", methods=["GET"])
def status() -> Response:
    logger.info("recieved request with args {}".format(json.dumps(request.args)))

    response = jsonify({"text": "ok"})
    response.headers.add("Access-Control-Allow-Origin", "*")

    return typing.cast(Response, response)
