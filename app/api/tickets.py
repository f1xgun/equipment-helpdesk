from typing import Annotated

from fastapi import Depends
from fastapi.routing import APIRouter

from app.dependencies import get_ticket_service
from app.models.ticket import Ticket
from app.schemas.ticket import TicketCreate, TicketResponse
from app.services.ticket import TicketService


router = APIRouter(prefix = "/tickets", tags=["tickets"])

@router.post("", response_model=TicketResponse, status_code=201)
def create_ticket(
    payload: TicketCreate,
    service: Annotated[TicketService, Depends(get_ticket_service)]
):
    ticket = Ticket(**payload.model_dump())
    return service.create(ticket)
