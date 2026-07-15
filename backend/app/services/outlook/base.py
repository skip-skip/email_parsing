from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime

from backend.app.services.outlook.models import (
    EmailMessage,
    FreeBusyInfo,
    OutlookCalendarEvent,
)


class EmailProvider(ABC):
    """Abstract interface for email retrieval and sending operations.

    Implementations isolate the application from specific email service
    details (e.g., Outlook COM, Microsoft Graph). Only this interface
    should be used by the rest of the system.
    """

    @abstractmethod
    async def get_new_messages(self) -> list[EmailMessage]:
        """Retrieve new (unread) messages from the inbox."""
        ...

    @abstractmethod
    async def get_conversation(self, conversation_id: str) -> list[EmailMessage]:
        """Retrieve all messages in a conversation thread."""
        ...

    @abstractmethod
    async def send_reply(self, conversation_id: str, body: str) -> None:
        """Send a reply to an existing conversation thread."""
        ...

    @abstractmethod
    async def send_reply_all(self, conversation_id: str, body: str) -> None:
        """Send a reply-all to an existing conversation thread."""
        ...

    @abstractmethod
    async def send_new_email(
        self, to: str, subject: str, body: str, conversation_id: str | None = None
    ) -> None:
        """Send a new email to the specified recipient.

        If conversation_id is provided, the email is sent as a reply-all
        to the last message in that conversation thread, preserving the
        thread in Outlook.
        """
        ...

    @abstractmethod
    async def get_message_by_entry_id(self, entry_id: str) -> EmailMessage | None:
        """Retrieve a single message by its Outlook EntryID."""
        ...


class CalendarProvider(ABC):
    """Abstract interface for calendar operations.

    Implementations isolate the application from specific calendar service
    details (e.g., Outlook COM, Microsoft Graph).
    """

    @abstractmethod
    async def get_events(
        self, start: datetime, end: datetime
    ) -> list[OutlookCalendarEvent]:
        """Retrieve calendar events within a time range."""
        ...

    @abstractmethod
    async def get_free_busy(
        self, start: datetime, end: datetime
    ) -> FreeBusyInfo:
        """Query free/busy information for a time range."""
        ...

    @abstractmethod
    async def create_event(
        self, title: str, start: datetime, end: datetime, body: str = ""
    ) -> str:
        """Create a new calendar event and return its ID."""
        ...

    @abstractmethod
    async def update_event(
        self, event_id: str, fields: dict[str, object]
    ) -> None:
        """Update fields on an existing calendar event."""
        ...

    @abstractmethod
    async def delete_event(self, event_id: str) -> None:
        """Delete a calendar event by ID."""
        ...
