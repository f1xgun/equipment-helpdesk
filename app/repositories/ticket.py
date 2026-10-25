from sqlalchemy.orm import Session

from app.models.ticket import Ticket


class TicketRepository:
    def __init__(self, session: Session):
        self.session = session

    def add(self, ticket: Ticket) -> Ticket:
        self.session.add(ticket)
        self.session.flush()
        return ticket

    def get_by_id(self, ticket_id: int) -> Ticket | None:
        return self.session.get(Ticket, ticket_id)
