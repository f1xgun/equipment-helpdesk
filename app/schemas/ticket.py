from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.ticket import TicketPriority, TicketStatus


class TicketCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    device_code: str = Field(min_length=1, max_length=64)
    room: str = Field(min_length=1, max_length=32)
    description: str = Field(min_length=1, max_length=2000)
    priority: TicketPriority = TicketPriority.NORMAL


class TicketResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    device_code: str
    room: str
    description: str
    priority: TicketPriority
    status: TicketStatus
    resolution: str | None
    created_at: datetime
    closed_at: datetime | None
