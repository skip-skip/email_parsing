from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Float, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.services.database.base import Base

if TYPE_CHECKING:
    from backend.app.models.ticket import Ticket


class CalendarEvent(Base):
    __tablename__ = "calendar_events"

    calendar_event_id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, default=uuid.uuid4
    )
    ticket_id: Mapped[uuid.UUID] = mapped_column(index=True)
    outlook_event_id: Mapped[str | None] = mapped_column(String, nullable=True)
    start_time: Mapped[datetime] = mapped_column()
    end_time: Mapped[datetime] = mapped_column()
    duration: Mapped[float] = mapped_column(Float)
    status: Mapped[str] = mapped_column(String, default="PROPOSED")
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    ticket: Mapped[Ticket] = relationship(lazy="select")
