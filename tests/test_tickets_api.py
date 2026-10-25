import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select

from app.models.ticket import Ticket
from app_final import app

pytestmark = pytest.mark.usefixtures("isolated_database")


def test_create_ticket_saves_it_to_database():
    payload = {
        "device_code": "PC-014",
        "room": "305Б",
        "description": "Монитор не включается",
    }

    with TestClient(app) as client:
        response = client.post("/tickets", json=payload)

        assert response.status_code == 201
        data = response.json()
        assert data["id"] > 0
        assert data["device_code"] == payload["device_code"]
        assert data["room"] == payload["room"]
        assert data["description"] == payload["description"]
        assert data["priority"] == "normal"
        assert data["status"] == "open"
        assert data["resolution"] is None
        assert data["closed_at"] is None
        assert data["created_at"]

        with app.state.session_factory() as session:
            saved = session.get(Ticket, data["id"])
            assert saved is not None
            assert saved.device_code == payload["device_code"]
            assert saved.description == payload["description"]


def test_create_ticket_rejects_blank_description():
    with TestClient(app) as client:
        response = client.post(
            "/tickets",
            json={
                "device_code": "PC-014",
                "room": "305Б",
                "description": "   ",
            },
        )

        assert response.status_code == 422
        assert any(
            error["loc"] == ["body", "description"]
            for error in response.json()["detail"]
        )
        with app.state.session_factory() as session:
            assert session.scalar(select(Ticket)) is None
