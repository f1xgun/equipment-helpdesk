from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.db.base import Base
from app.models.ticket import Ticket, TicketPriority, TicketStatus
from app.repositories.ticket import TicketRepository


def test_repository_saves_and_finds_ticket(tmp_path):
    engine = create_engine(f"sqlite:///{tmp_path / 'test.db'}")
    try:
        Base.metadata.create_all(engine)

        with Session(engine) as session:
            repository = TicketRepository(session)
            ticket = repository.add(
                Ticket(device_code="DC123", room="N123", description="printer is broken")
            )
            ticket_id = ticket.id
            assert ticket_id is not None
            session.commit()

        with Session(engine) as session:
            repository = TicketRepository(session)
            saved = repository.get_by_id(ticket_id)

            assert saved is not None
            assert saved.device_code == "DC123"
            assert saved.room == "N123"
            assert saved.description == "printer is broken"
            assert saved.priority is TicketPriority.NORMAL
            assert saved.status is TicketStatus.OPEN
            assert saved.resolution is None
            assert saved.closed_at is None
            assert saved.created_at is not None
            assert repository.get_by_id(ticket_id + 1) is None
    finally:
        engine.dispose()
