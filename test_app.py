from fastapi.testclient import TestClient

from app_final import VERSION, app


def test_health():
    with TestClient(app) as client:
        response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_version():
    with TestClient(app) as client:
        response = client.get("/version")

    assert response.status_code == 200
    assert response.json() == {"version": VERSION}
