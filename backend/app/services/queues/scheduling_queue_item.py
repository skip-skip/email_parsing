from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime

from backend.app.agents.calendar_planning_agent import ScheduleSuggestion
from backend.app.services.confidence import (
    classify_confidence,
    get_confidence_indicator,
)


@dataclass
class SchedulingQueueItem:
    ticket_id: uuid.UUID
    suggestion: ScheduleSuggestion
    confidence: float = 0.0
    status: str = "PENDING"
    created_at: datetime = field(default_factory=datetime.now)

    @property
    def confidence_level(self) -> str:
        return classify_confidence(self.confidence)

    @property
    def confidence_indicator(self) -> dict[str, str]:
        return get_confidence_indicator(self.confidence)
