import json

import pytest

import service_template.app.http as module


@pytest.fixture
def client():
    client = module.app.test_client()

    yield client


def test_create_poll_http(mocker, client):
    result = client.get("/api/v0/status", data={"foo": "bar"})

    assert result.status_code == 200
    assert json.loads(result.data) == {"text": "ok"}
