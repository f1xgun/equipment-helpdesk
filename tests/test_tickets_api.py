from datetime import datetime

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select

from app.models.ticket import Ticket, TicketStatus
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

        fetched = client.get(f"/tickets/{data['id']}")
        assert fetched.status_code == 200
        assert fetched.json() == data

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


def test_get_missing_ticket_returns_404():
    with TestClient(app) as client:
        response = client.get("/tickets/999")

    assert response.status_code == 404
    assert response.json() == {"detail": "Ticket not found"}


def test_list_tickets_with_filters():
    with TestClient(app) as client:
        with app.state.session_factory() as session:
            tickets = [
                Ticket(device_code="PC-001", room="305Б", description="Нет изображения"),
                Ticket(device_code="PC-002", room="306", description="Не работает мышь"),
                Ticket(
                    device_code="PC-003",
                    room="305Б",
                    description="Нет сети",
                    status=TicketStatus.IN_PROGRESS,
                ),
            ]
            session.add_all(tickets)
            session.commit()
            first_id, second_id, third_id = [ticket.id for ticket in tickets]

        response = client.get("/tickets")
        assert response.status_code == 200
        assert [ticket["id"] for ticket in response.json()] == [
            first_id,
            second_id,
            third_id,
        ]

        response = client.get("/tickets", params={"room": "305Б"})
        assert response.status_code == 200
        assert [ticket["id"] for ticket in response.json()] == [first_id, third_id]

        response = client.get("/tickets", params={"status": "open"})
        assert response.status_code == 200
        assert [ticket["id"] for ticket in response.json()] == [first_id, second_id]

        response = client.get("/tickets", params={"status": "open", "room": "305Б"})
        assert response.status_code == 200
        assert [ticket["id"] for ticket in response.json()] == [first_id]

        response = client.get("/tickets", params={"room": "999"})
        assert response.status_code == 200
        assert response.json() == []

        response = client.get("/tickets", params={"status": "unknown"})
        assert response.status_code == 422


def test_ticket_can_be_taken_into_work_and_closed():
    with TestClient(app) as client:
        created = client.post(
            "/tickets",
            json={
                "device_code": "PC-014",
                "room": "305Б",
                "description": "Монитор не включается",
            },
        )
        assert created.status_code == 201
        ticket = created.json()
        status_url = f"/tickets/{ticket['id']}/status"

        response = client.patch(status_url, json={"status": "in_progress"})
        assert response.status_code == 200
        assert response.json()["status"] == "in_progress"
        assert response.json()["resolution"] is None
        assert response.json()["closed_at"] is None

        response = client.patch(
            status_url,
            json={"status": "closed", "resolution": "  Заменён кабель питания  "},
        )
        assert response.status_code == 200
        closed = response.json()
        assert closed["status"] == "closed"
        assert closed["resolution"] == "Заменён кабель питания"
        assert closed["created_at"] == ticket["created_at"]
        assert datetime.fromisoformat(closed["closed_at"]) >= datetime.fromisoformat(
            ticket["created_at"]
        )
        assert client.get(f"/tickets/{ticket['id']}").json() == closed

        response = client.patch(status_url, json={"status": "in_progress"})
        assert response.status_code == 409
        assert client.get(f"/tickets/{ticket['id']}").json() == closed


def test_invalid_status_changes_do_not_modify_ticket():
    with TestClient(app) as client:
        response = client.post(
            "/tickets",
            json={
                "device_code": "PC-014",
                "room": "305Б",
                "description": "Монитор не включается",
            },
        )
        assert response.status_code == 201
        ticket = response.json()
        ticket_url = f"/tickets/{ticket['id']}"
        status_url = f"{ticket_url}/status"

        response = client.patch(
            status_url, json={"status": "closed", "resolution": "Заменён кабель"}
        )
        assert response.status_code == 409
        assert client.get(ticket_url).json() == ticket

        response = client.patch(
            status_url,
            json={"status": "in_progress", "resolution": "Ремонт ещё не завершён"},
        )
        assert response.status_code == 422
        assert client.get(ticket_url).json() == ticket

        response = client.patch(status_url, json={"status": "in_progress"})
        assert response.status_code == 200
        in_progress = response.json()

        response = client.patch(status_url, json={"status": "closed"})
        assert response.status_code == 422
        assert response.json()["detail"] == "Resolution is required to close a ticket"

        response = client.patch(
            status_url, json={"status": "closed", "resolution": "   "}
        )
        assert response.status_code == 422
        assert client.get(ticket_url).json() == in_progress

        response = client.patch(
            "/tickets/999/status", json={"status": "in_progress"}
        )
        assert response.status_code == 404
        assert response.json() == {"detail": "Ticket not found"}
