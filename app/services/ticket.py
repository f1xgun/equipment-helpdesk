from sqlalchemy.orm import Session

from app.models.ticket import Ticket, TicketStatus
from app.repositories.ticket import TicketRepository


class TicketNotFoundError(Exception):
    pass


class TicketService:
    def __init__(self, repository: TicketRepository, session: Session):
        self.repository = repository
        self.session = session

    def create(self, ticket: Ticket) -> Ticket:
        with self.session.begin():
            created = self.repository.add(ticket)

        return created

    def get_by_id(self, ticket_id: int) -> Ticket:
        ticket = self.repository.get_by_id(ticket_id)
        if ticket is None:
            raise TicketNotFoundError()

        return ticket

    def get_with_filters(
        self,
        status: TicketStatus | None = None,
        room: str | None = None,
    ) -> list[Ticket]:
        tickets = self.repository.get_with_filters(status, room)
        return tickets
