from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import Float, JSON, String, func
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.services.database.base import Base


class SchedulingQueueRecord(Base):
    __tablename__ = "scheduling_queue"

    ticket_id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, default=uuid.uuid4
    )
    suggestion_json: Mapped[dict[str, Any]] = mapped_column(JSON)
    confidence: Mapped[float] = mapped_column(Float, default=0.0)
    status: Mapped[str] = mapped_column(
        String, default="PENDING", index=True
    )
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
