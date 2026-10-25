from sqlalchemy.orm import Session

from app.models.ticket import Ticket
from app.repositories.ticket import TicketRepository


class TicketService:
    def __init__(self, repository: TicketRepository, session: Session):
        self.repository = repository
        self.session = session

    def create(self, ticket: Ticket) -> Ticket:
        with self.session.begin():
            created = self.repository.add(ticket)

        return created
