import json

import pytest

import service_template.app.http as module


@pytest.fixture
def client():
    client = module.app.test_client()

    yield client


def test_status(mocker, client):
    result = client.get("/api/v0/status")

    assert result.status_code == 200
    assert json.loads(result.data) == {"text": "ok"}


def test_post(mocker, client):
    result = client.post("/api/v0/foo", data={"foo": "a", "bar": "b"})

    assert result.status_code == 200
    assert json.loads(result.data) == {"foo": "a", "bar": "b"}


def test_post_validation_fails(mocker, client):
    result = client.post("/api/v0/foo", data={"bar": "b"})

    assert result.status_code == 500


def test_get(mocker, client):
    result = client.get("/api/v0/foo?foo=a&bar=b")

    assert result.status_code == 200
    assert json.loads(result.data) == {"foo": "a", "bar": "b"}


def test_get_validation_fails(mocker, client):
    result = client.get("/api/v0/foo", data={"bar": "b"})

    assert result.status_code == 500
