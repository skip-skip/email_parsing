from __future__ import annotations

import asyncio
import logging
import time
from datetime import datetime

from backend.app.services.outlook.base import CalendarProvider
from backend.app.services.outlook.models import FreeBusyInfo, OutlookCalendarEvent

logger = logging.getLogger(__name__)

MAX_RETRIES = 3
RETRY_DELAY = 1.0


def _get_outlook_application():
    import pythoncom

    pythoncom.CoInitialize()
    import win32com.client

    return win32com.client.Dispatch("Outlook.Application")


def _get_namespace(app):
    return app.GetNamespace("MAPI")


def _get_calendar(namespace):
    return namespace.GetDefaultFolder(9)


def _map_com_appointment(appointment) -> OutlookCalendarEvent:
    return OutlookCalendarEvent(
        event_id=appointment.EntryID or "",
        title=appointment.Subject or "",
        start=appointment.Start,
        end=appointment.End,
        body=appointment.Body or "",
        is_all_day=appointment.AllDayEvent,
    )


class OutlookComCalendarProvider(CalendarProvider):
    def __init__(self) -> None:
        self._app = None
        self._namespace = None

    def _connect(self) -> None:
        self._app = _get_outlook_application()
        self._namespace = _get_namespace(self._app)

    def _connect_with_retry(self) -> None:
        last_error: Exception | None = None
        for attempt in range(MAX_RETRIES):
            try:
                self._connect()
                return
            except Exception as e:
                last_error = e
                logger.warning(
                    "Outlook connection attempt %d/%d failed: %s",
                    attempt + 1,
                    MAX_RETRIES,
                    e,
                )
                if attempt < MAX_RETRIES - 1:
                    time.sleep(RETRY_DELAY * (attempt + 1))
        raise ConnectionError(
            f"Failed to connect to Outlook after {MAX_RETRIES} attempts"
        ) from last_error

    def _fetch_events(
        self, start: datetime, end: datetime
    ) -> list[OutlookCalendarEvent]:
        calendar = _get_calendar(self._namespace)
        items = calendar.Items
        items.IncludeRecurrences = True
        items.Sort("[Start]")
        filter_str = f"[Start] >= '{start.strftime('%m/%d/%Y %I:%M %p')}' AND [End] <= '{end.strftime('%m/%d/%Y %I:%M %p')}'"
        restricted = items.Restrict(filter_str)
        return [_map_com_appointment(appt) for appt in restricted]

    def _fetch_free_busy(self, start: datetime, end: datetime) -> FreeBusyInfo:
        calendar = _get_calendar(self._namespace)
        items = calendar.Items
        items.IncludeRecurrences = True
        items.Sort("[Start]")
        filter_str = f"[Start] >= '{start.strftime('%m/%d/%Y %I:%M %p')}' AND [End] <= '{end.strftime('%m/%d/%Y %I:%M %p')}'"
        restricted = items.Restrict(filter_str)
        busy_periods = []
        for appt in restricted:
            if not appt.AllDayEvent:
                busy_periods.append((appt.Start, appt.End))
        return FreeBusyInfo(start=start, end=end, busy_periods=busy_periods)

    def _create_event(
        self, title: str, start: datetime, end: datetime, body: str = ""
    ) -> str:
        calendar = _get_calendar(self._namespace)
        appointment = calendar.Items.Add()
        appointment.Subject = title
        appointment.Start = start
        appointment.End = end
        appointment.Body = body
        appointment.ReminderSet = True
        appointment.ReminderMinutesBeforeStart = 15
        appointment.Save()
        entry_id = appointment.EntryID
        appointment.Send()
        return entry_id

    def _update_event(
        self, event_id: str, fields: dict[str, object]
    ) -> None:
        try:
            appointment = self._namespace.GetItemFromID(event_id)
            if "title" in fields:
                appointment.Subject = fields["title"]
            if "start" in fields:
                appointment.Start = fields["start"]
            if "end" in fields:
                appointment.End = fields["end"]
            if "body" in fields:
                appointment.Body = fields["body"]
            appointment.Save()
        except Exception:
            logger.warning("Failed to update event: %s", event_id)
            raise

    def _delete_event(self, event_id: str) -> None:
        try:
            appointment = self._namespace.GetItemFromID(event_id)
            appointment.Delete()
        except Exception:
            logger.warning("Failed to delete event: %s", event_id)
            raise

    async def get_events(
        self, start: datetime, end: datetime
    ) -> list[OutlookCalendarEvent]:
        def _fetch():
            self._connect_with_retry()
            return self._fetch_events(start, end)

        return await asyncio.to_thread(_fetch)

    async def get_free_busy(
        self, start: datetime, end: datetime
    ) -> FreeBusyInfo:
        def _fetch():
            self._connect_with_retry()
            return self._fetch_free_busy(start, end)

        return await asyncio.to_thread(_fetch)

    async def create_event(
        self, title: str, start: datetime, end: datetime, body: str = ""
    ) -> str:
        def _create():
            self._connect_with_retry()
            return self._create_event(title, start, end, body)

        return await asyncio.to_thread(_create)

    async def update_event(
        self, event_id: str, fields: dict[str, object]
    ) -> None:
        def _update():
            self._connect_with_retry()
            self._update_event(event_id, fields)

        await asyncio.to_thread(_update)

    async def delete_event(self, event_id: str) -> None:
        def _delete():
            self._connect_with_retry()
            self._delete_event(event_id)

        await asyncio.to_thread(_delete)
