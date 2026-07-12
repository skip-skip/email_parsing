from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime

from backend.app.agents.email_draft_agent import DraftEmail
from backend.app.services.confidence import (
    classify_confidence,
    get_confidence_indicator,
)


@dataclass
class QueueItem:
    ticket_id: uuid.UUID
    draft_email: DraftEmail
    missing_fields: list[str]
    confidence: float = 0.0
    created_at: datetime = field(default_factory=datetime.now)
    status: str = "PENDING"

    @property
    def confidence_level(self) -> str:
        return classify_confidence(self.confidence)

    @property
    def confidence_indicator(self) -> dict[str, str]:
        return get_confidence_indicator(self.confidence)
