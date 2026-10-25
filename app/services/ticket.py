import logging
from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.models.ticket import Ticket, TicketStatus
from app.repositories.ticket import TicketRepository

logger = logging.getLogger(__name__)


class TicketNotFoundError(Exception):
    pass


class InvalidStatusTransitionError(Exception):
    pass


class InvalidResolutionError(Exception):
    pass


class TicketService:
    def __init__(self, repository: TicketRepository, session: Session):
        self.repository = repository
        self.session = session

    def create(self, ticket: Ticket) -> Ticket:
        with self.session.begin():
            created = self.repository.add(ticket)

        logger.info(
            "Ticket created: id=%s priority=%s", created.id, created.priority.value
        )
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

    def change_status(
        self,
        ticket_id: int,
        status: TicketStatus,
        resolution: str | None = None,
    ) -> Ticket:
        with self.session.begin():
            ticket = self.get_by_id(ticket_id)
            previous_status = ticket.status
            allowed_transitions = {
                TicketStatus.OPEN: TicketStatus.IN_PROGRESS,
                TicketStatus.IN_PROGRESS: TicketStatus.CLOSED,
            }
            if allowed_transitions.get(ticket.status) != status:
                raise InvalidStatusTransitionError(
                    f"Cannot change status from {ticket.status.value} to {status.value}"
                )

            if status == TicketStatus.CLOSED:
                if resolution is None or not resolution.strip():
                    raise InvalidResolutionError("Resolution is required to close a ticket")
                ticket.resolution = resolution.strip()
                ticket.closed_at = datetime.now(UTC).replace(tzinfo=None)
            elif resolution is not None:
                raise InvalidResolutionError(
                    "Resolution can only be provided when closing a ticket"
                )

            ticket.status = status

        logger.info(
            "Ticket status changed: id=%s %s -> %s",
            ticket.id,
            previous_status.value,
            ticket.status.value,
        )
        return ticket
