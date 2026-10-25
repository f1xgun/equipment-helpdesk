

from typing import Annotated

from fastapi import Depends, Request
from sqlalchemy.orm import Session

from app.repositories.ticket import TicketRepository
from app.services.ticket import TicketService


def get_session(request: Request):
    session_factory = request.app.state.session_factory

    with session_factory() as session:
        yield session


def get_ticket_service(
    session: Annotated[Session, Depends(get_session)],
) -> TicketService:
    repository = TicketRepository(session)
    return TicketService(repository, session)
