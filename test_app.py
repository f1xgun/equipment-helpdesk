import logging

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session

from app_final import VERSION, app

pytestmark = pytest.mark.usefixtures("isolated_database")


def test_health(caplog):
    caplog.set_level(logging.INFO, logger="app_final")
    with TestClient(app) as client:
        response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
    assert "Equipment Helpdesk started:" in caplog.text
    assert "Equipment Helpdesk stopped" in caplog.text


def test_version():
    with TestClient(app) as client:
        response = client.get("/version")

    assert response.status_code == 200
    assert response.json() == {"version": VERSION}


def test_health_returns_503_when_database_is_unavailable(monkeypatch, caplog):
    def fail_execute(self, *args, **kwargs):
        raise OperationalError("SELECT 1", {}, Exception("Internal database details"))

    with TestClient(app) as client:
        monkeypatch.setattr(Session, "execute", fail_execute)
        response = client.get("/health")

    assert response.status_code == 503
    assert response.json() == {"detail": "Database unavailable"}
    assert "Database health check failed (OperationalError)" in caplog.text
    assert "Internal database details" not in caplog.text
