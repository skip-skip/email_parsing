from enum import StrEnum
from typing import Any, TypedDict


class WorkflowState(TypedDict):
    ticket_id: str
    status: str
    parsed_data: dict[str, Any] | None
    validation_result: dict[str, Any] | None
    missing_fields: list[str]
    error: str | None


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
