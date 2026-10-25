from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.ticket import Ticket, TicketStatus


class TicketRepository:
    def __init__(self, session: Session):
        self.session = session

    def add(self, ticket: Ticket) -> Ticket:
        self.session.add(ticket)
        self.session.flush()
        return ticket

    def get_by_id(self, ticket_id: int) -> Ticket | None:
        return self.session.get(Ticket, ticket_id)

    def get_with_filters(self, status: TicketStatus | None = None, room: str | None = None) -> list[Ticket]:
        query = select(Ticket).order_by(Ticket.id)

        if status is not None:
            query = query.where(Ticket.status == status)

        if room is not None:
            query = query.where(Ticket.room == room)

        return list(self.session.scalars(query))
