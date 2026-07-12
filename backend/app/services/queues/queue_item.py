from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime

from backend.app.agents.email_draft_agent import DraftEmail


@dataclass
class QueueItem:
    ticket_id: uuid.UUID
    draft_email: DraftEmail
    missing_fields: list[str]
    created_at: datetime = field(default_factory=datetime.now)
    status: str = "PENDING"
