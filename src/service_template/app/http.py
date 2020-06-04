import logging
import json

from flask import Flask, jsonify, request, Response
from raven import Client
from raven.contrib.flask import Sentry
from raven.transport.requests import RequestsHTTPTransport


app = Flask(__name__)
sentry = Sentry(app, client=Client(transport=RequestsHTTPTransport,),)
logger = logging.getLogger(__name__)


@app.route("/api/v0/example", methods=["GET"])
def example() -> Response:
    logger.info("hi {}".format(json.dumps(request.args)))

    response = jsonify({"text": "ok"})
    response.headers.add("Access-Control-Allow-Origin", "*")

    return response
