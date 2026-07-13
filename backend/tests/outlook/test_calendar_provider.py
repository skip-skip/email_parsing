from __future__ import annotations

from datetime import datetime
from unittest.mock import MagicMock, patch

from backend.app.services.outlook.com_calendar_provider import (
    OutlookComCalendarProvider,
)
from backend.tests.outlook.mock_com import MockAppointmentItem, MockOutlookApp


class TestOutlookComCalendarProvider:
    @patch("backend.app.services.outlook.com_calendar_provider._get_outlook_application")
    def test_get_events(self, mock_get_app: MagicMock) -> None:
        mock_app = MockOutlookApp()
        mock_get_app.return_value = mock_app

        appt1 = MockAppointmentItem(EntryID="appt-1", Subject="Meeting")
        appt2 = MockAppointmentItem(EntryID="appt-2", Subject="Lunch")
        mock_app._namespace._calendar._items.items = [appt1, appt2]

        provider = OutlookComCalendarProvider()
        provider._namespace = mock_app._namespace
        start = datetime(2026, 1, 1)
        end = datetime(2026, 12, 31)
        events = provider._fetch_events(start, end)

        assert len(events) == 2
        assert events[0].event_id == "appt-1"
        assert events[1].event_id == "appt-2"

    @patch("backend.app.services.outlook.com_calendar_provider._get_outlook_application")
    def test_get_free_busy(self, mock_get_app: MagicMock) -> None:
        mock_app = MockOutlookApp()
        mock_get_app.return_value = mock_app

        appt = MockAppointmentItem(AllDayEvent=False)
        mock_app._namespace._calendar._items.items = [appt]

        provider = OutlookComCalendarProvider()
        provider._namespace = mock_app._namespace
        start = datetime(2026, 1, 1)
        end = datetime(2026, 12, 31)
        free_busy = provider._fetch_free_busy(start, end)

        assert free_busy.start == start
        assert free_busy.end == end
        assert len(free_busy.busy_periods) == 1

    @patch("backend.app.services.outlook.com_calendar_provider._get_outlook_application")
    def test_create_event(self, mock_get_app: MagicMock) -> None:
        mock_app = MockOutlookApp()
        mock_get_app.return_value = mock_app

        provider = OutlookComCalendarProvider()
        provider._namespace = mock_app._namespace
        start = datetime(2026, 7, 15, 10, 0)
        end = datetime(2026, 7, 15, 11, 0)
        event_id = provider._create_event("Test Event", start, end, "Test body")

        assert event_id == "appt-001"

    @patch("backend.app.services.outlook.com_calendar_provider._get_outlook_application")
    def test_update_event(self, mock_get_app: MagicMock) -> None:
        mock_app = MockOutlookApp()
        mock_get_app.return_value = mock_app

        appt = MockAppointmentItem(EntryID="appt-1")
        mock_app._namespace._calendar._items.items = [appt]

        provider = OutlookComCalendarProvider()
        provider._namespace = mock_app._namespace
        provider._update_event("appt-1", {"title": "Updated Event"})

    @patch("backend.app.services.outlook.com_calendar_provider._get_outlook_application")
    def test_delete_event(self, mock_get_app: MagicMock) -> None:
        mock_app = MockOutlookApp()
        mock_get_app.return_value = mock_app

        appt = MockAppointmentItem(EntryID="appt-1")
        mock_app._namespace._calendar._items.items = [appt]

        provider = OutlookComCalendarProvider()
        provider._namespace = mock_app._namespace
        provider._delete_event("appt-1")
