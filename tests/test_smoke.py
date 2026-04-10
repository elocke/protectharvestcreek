from fastapi.testclient import TestClient

from app import app


def test_healthz():
    with TestClient(app) as client:
        resp = client.get("/healthz")
        assert resp.status_code == 200
        assert resp.json() == {"status": "ok"}


def test_index_renders():
    with TestClient(app) as client:
        resp = client.get("/")
        assert resp.status_code == 200
        assert "text/html" in resp.headers["content-type"]


def test_whats_going_on_renders():
    with TestClient(app) as client:
        resp = client.get("/whats-going-on")
        assert resp.status_code == 200
