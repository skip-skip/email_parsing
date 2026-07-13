from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Float, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.services.database.base import Base

if TYPE_CHECKING:
    from backend.app.models.email import Email


class Ticket(Base):
    __tablename__ = "tickets"

    ticket_id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, default=uuid.uuid4
    )
    status: Mapped[str] = mapped_column(
        String, default="NEW", index=True
    )
    client: Mapped[str | None] = mapped_column(String, nullable=True, index=True)
    contact: Mapped[str | None] = mapped_column(String, nullable=True)
    project_number: Mapped[str | None] = mapped_column(String, nullable=True)
    task_description: Mapped[str | None] = mapped_column(Text, nullable=True)
    deadline: Mapped[datetime | None] = mapped_column(nullable=True, index=True)
    budget_hours: Mapped[float | None] = mapped_column(Float, nullable=True)
    estimated_hours: Mapped[float | None] = mapped_column(Float, nullable=True)
    priority: Mapped[int] = mapped_column(Integer, default=0, index=True)
    calendar_event_id: Mapped[str | None] = mapped_column(String, nullable=True)
    conversation_id: Mapped[str | None] = mapped_column(
        String, nullable=True, index=True
    )
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime | None] = mapped_column(
        nullable=True, onupdate=func.now()
    )

    emails: Mapped[list[Email]] = relationship(
        back_populates="ticket", lazy="selectin"
    )
