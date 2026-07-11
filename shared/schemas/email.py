from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class EmailMessage(BaseModel):
    email_id: UUID
    conversation_id: str
    entry_id: str
    sender: str
    subject: str
    body: str
    received_time: datetime
    attachments: list[str] = []


class ParsedEmail(BaseModel):
    client: str | None = None
    sender: str
    subject: str
    project_number: str | None = None
    task_description: str | None = None
    deadline: datetime | None = None
    budget_hours: float | None = None
    attachments: list[str] = []
    confidence: float = 0.0
