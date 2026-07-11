from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class EmailMessage:
    conversation_id: str
    entry_id: str
    sender: str
    subject: str
    body: str
    received_time: datetime
    attachments: list[str] = field(default_factory=list)
    email_id: str | None = None


@dataclass
class FreeBusyInfo:
    start: datetime
    end: datetime
    busy_periods: list[tuple[datetime, datetime]] = field(default_factory=list)


@dataclass
class OutlookCalendarEvent:
    event_id: str
    title: str
    start: datetime
    end: datetime
    body: str = ""
    is_all_day: bool = False
