from typing import Annotated

from fastapi import Depends, HTTPException
from fastapi.routing import APIRouter

from app.dependencies import get_ticket_service
from app.models.ticket import Ticket, TicketStatus
from app.schemas.ticket import TicketCreate, TicketResponse, TicketStatusUpdate
from app.services.ticket import (
    InvalidResolutionError,
    InvalidStatusTransitionError,
    TicketNotFoundError,
    TicketService,
)

router = APIRouter(prefix = "/tickets", tags=["tickets"])

@router.post("", response_model=TicketResponse, status_code=201)
def create_ticket(
    payload: TicketCreate,
    service: Annotated[TicketService, Depends(get_ticket_service)]
):
    ticket = Ticket(**payload.model_dump())
    return service.create(ticket)


@router.get("/{ticket_id}", response_model=TicketResponse)
def get_by_id(
    ticket_id: int,
    service: Annotated[TicketService, Depends(get_ticket_service)],
):
    try:
        ticket = service.get_by_id(ticket_id)
        return ticket
    except TicketNotFoundError:
        raise HTTPException(status_code=404, detail="Ticket not found") from None


@router.get("", response_model=list[TicketResponse])
def get_with_filters(
    service: Annotated[TicketService, Depends(get_ticket_service)],
    status: TicketStatus | None = None,
    room: str | None = None,
):
    return service.get_with_filters(status=status, room=room)


@router.patch("/{ticket_id}/status", response_model=TicketResponse)
def change_status(
    ticket_id: int,
    payload: TicketStatusUpdate,
    service: Annotated[TicketService, Depends(get_ticket_service)],
):
    try:
        return service.change_status(ticket_id, **payload.model_dump())
    except TicketNotFoundError:
        raise HTTPException(status_code=404, detail="Ticket not found") from None
    except InvalidStatusTransitionError as error:
        raise HTTPException(status_code=409, detail=str(error)) from None
    except InvalidResolutionError as error:
        raise HTTPException(status_code=422, detail=str(error)) from None
