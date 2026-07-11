from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import JSON, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.services.database.base import Base

if TYPE_CHECKING:
    from backend.app.models.ticket import Ticket


class Email(Base):
    __tablename__ = "emails"

    email_id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, default=uuid.uuid4
    )
    conversation_id: Mapped[str] = mapped_column(String, index=True)
    entry_id: Mapped[str] = mapped_column(String, unique=True)
    sender: Mapped[str] = mapped_column(String)
    subject: Mapped[str] = mapped_column(String)
    body: Mapped[str] = mapped_column(Text)
    received_time: Mapped[datetime] = mapped_column()
    attachments: Mapped[list] = mapped_column(JSON, default=list)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    ticket_id: Mapped[uuid.UUID | None] = mapped_column(
        nullable=True, index=True
    )

    ticket: Mapped[Ticket | None] = relationship(
        back_populates="emails", lazy="select"
    )
