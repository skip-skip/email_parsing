from datetime import datetime
from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel


class TicketStatus(StrEnum):
    NEW = "NEW"
    PARSED = "PARSED"
    VALIDATED = "VALIDATED"
    WAITING_FOR_INFORMATION = "WAITING_FOR_INFORMATION"
    READY_FOR_SCHEDULING = "READY_FOR_SCHEDULING"
    PENDING_USER_APPROVAL = "PENDING_USER_APPROVAL"
    ACCEPTED = "ACCEPTED"
    CALENDAR_CREATED = "CALENDAR_CREATED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    ARCHIVED = "ARCHIVED"


class TicketCreate(BaseModel):
    client: str
    contact: str
    project_number: str | None = None
    task_description: str
    deadline: datetime | None = None
    budget_hours: float | None = None
    estimated_hours: float | None = None
    priority: int = 0
    conversation_id: str | None = None


class TicketUpdate(BaseModel):
    status: TicketStatus | None = None
    client: str | None = None
    contact: str | None = None
    project_number: str | None = None
    task_description: str | None = None
    deadline: datetime | None = None
    budget_hours: float | None = None
    estimated_hours: float | None = None
    priority: int | None = None
    calendar_event_id: UUID | None = None
    conversation_id: str | None = None


class TicketResponse(BaseModel):
    ticket_id: UUID
    status: TicketStatus
    client: str
    contact: str
    project_number: str | None = None
    task_description: str
    deadline: datetime | None = None
    budget_hours: float | None = None
    estimated_hours: float | None = None
    priority: int = 0
    calendar_event_id: UUID | None = None
    conversation_id: str | None = None
    created_at: datetime
    updated_at: datetime
