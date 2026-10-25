from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.db.base import Base
from app.models.ticket import Ticket, TicketPriority, TicketStatus


def test_ticket_survives_new_session(tmp_path):
    engine = create_engine(f"sqlite:///{tmp_path / 'test.db'}")
    try:
        Base.metadata.create_all(engine)

        with Session(engine) as session:
            ticket = Ticket(
                device_code="DC123", room="N123", description="printer is broken"
            )
            session.add(ticket)
            session.flush()
            ticket_id = ticket.id
            session.commit()

        with Session(engine) as session:
            saved = session.get(Ticket, ticket_id)

            assert saved is not None
            assert saved.device_code == "DC123"
            assert saved.room == "N123"
            assert saved.description == "printer is broken"
            assert saved.priority is TicketPriority.NORMAL
            assert saved.status is TicketStatus.OPEN
            assert saved.resolution is None
            assert saved.closed_at is None
            assert saved.created_at is not None
    finally:
        engine.dispose()
