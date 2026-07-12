from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime

from backend.app.agents.calendar_planning_agent import ScheduleSuggestion


@dataclass
class SchedulingQueueItem:
    ticket_id: uuid.UUID
    suggestion: ScheduleSuggestion
    status: str = "PENDING"
    created_at: datetime = field(default_factory=datetime.now)
