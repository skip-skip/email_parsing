from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime

from backend.app.services.outlook.models import (
    EmailMessage,
    FreeBusyInfo,
    OutlookCalendarEvent,
)


class EmailProvider(ABC):
    @abstractmethod
    async def get_new_messages(self) -> list[EmailMessage]: ...

    @abstractmethod
    async def get_conversation(self, conversation_id: str) -> list[EmailMessage]: ...

    @abstractmethod
    async def send_reply(self, conversation_id: str, body: str) -> None: ...

    @abstractmethod
    async def get_message_by_entry_id(self, entry_id: str) -> EmailMessage | None: ...


class CalendarProvider(ABC):
    @abstractmethod
    async def get_events(
        self, start: datetime, end: datetime
    ) -> list[OutlookCalendarEvent]: ...

    @abstractmethod
    async def get_free_busy(
        self, start: datetime, end: datetime
    ) -> FreeBusyInfo: ...

    @abstractmethod
    async def create_event(
        self, title: str, start: datetime, end: datetime, body: str = ""
    ) -> str: ...

    @abstractmethod
    async def update_event(
        self, event_id: str, fields: dict[str, object]
    ) -> None: ...

    @abstractmethod
    async def delete_event(self, event_id: str) -> None: ...
