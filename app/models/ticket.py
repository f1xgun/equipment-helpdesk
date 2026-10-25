from datetime import UTC, datetime
from enum import StrEnum

from sqlalchemy import DateTime, String, Text
from sqlalchemy import Enum as SQLAlchemyEnum
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class TicketPriority(StrEnum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"


class TicketStatus(StrEnum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    CLOSED = "closed"


class Ticket(Base):
    __tablename__ = "tickets"

    id: Mapped[int] = mapped_column(primary_key=True)
    device_code: Mapped[str] = mapped_column(String(64))
    room: Mapped[str] = mapped_column(String(32))
    description: Mapped[str] = mapped_column(Text)
    priority: Mapped[TicketPriority] = mapped_column(
        SQLAlchemyEnum(
            TicketPriority,
            values_callable=lambda enum: [item.value for item in enum],
            create_constraint=True,
        ),
        default=TicketPriority.NORMAL,
    )
    status: Mapped[TicketStatus] = mapped_column(
        SQLAlchemyEnum(
            TicketStatus,
            values_callable=lambda enum: [item.value for item in enum],
            create_constraint=True,
        ),
        default=TicketStatus.OPEN,
    )
    resolution: Mapped[str | None] = mapped_column(Text, nullable=True)
    # Dates are stored as UTC without timezone information.
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(UTC).replace(tzinfo=None),
    )
    closed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
