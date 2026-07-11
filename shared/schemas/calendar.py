from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class CalendarEvent(BaseModel):
    calendar_event_id: UUID
    ticket_id: UUID
    start_time: datetime
    end_time: datetime
    duration: float
    status: str


class ScheduleBlock(BaseModel):
    day: str
    start_time: datetime
    end_time: datetime
    duration: float
    calendar_event_id: UUID | None = None
