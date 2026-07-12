from __future__ import annotations

import asyncio
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

from backend.app.agents.calendar_planning_agent import ScheduleBlock
from backend.app.services.scheduler.calendar_manager import (
    CalendarEvent,
    CalendarManager,
)


class TestCalendarManager:
    def _make_blocks(self) -> list[ScheduleBlock]:
        now = datetime.now()
        return [
            ScheduleBlock(
                start_time=now.replace(hour=9, minute=0),
                end_time=now.replace(hour=13, minute=0),
                hours=4.0,
                description="Morning work block",
            )
        ]

    @patch("backend.app.services.scheduler.calendar_manager.async_session_factory")
    def test_create_events(self, mock_session_factory: MagicMock) -> None:
        mock_session = AsyncMock()
        mock_session_factory.return_value.__aenter__.return_value = mock_session

        mock_ticket_repo = MagicMock()
        mock_ticket_repo.update = AsyncMock()

        with patch("backend.app.services.scheduler.calendar_manager.TicketRepository", return_value=mock_ticket_repo):
            manager = CalendarManager()
            blocks = self._make_blocks()
            events = asyncio.run(
                manager.create_events("550e8400-e29b-41d4-a716-446655440000", blocks, "Test Task")
            )

        assert len(events) == 1
        assert isinstance(events[0], CalendarEvent)
        assert events[0].subject == "Test Task"

    @patch("backend.app.services.scheduler.calendar_manager.async_session_factory")
    def test_cancel_events(self, mock_session_factory: MagicMock) -> None:
        mock_session = AsyncMock()
        mock_session_factory.return_value.__aenter__.return_value = mock_session

        mock_ticket_repo = MagicMock()
        mock_ticket_repo.update = AsyncMock()

        with patch("backend.app.services.scheduler.calendar_manager.TicketRepository", return_value=mock_ticket_repo):
            manager = CalendarManager()
            blocks = self._make_blocks()
            asyncio.run(
                manager.create_events("550e8400-e29b-41d4-a716-446655440000", blocks, "Test Task")
            )
            asyncio.run(manager.cancel_events("550e8400-e29b-41d4-a716-446655440000"))
            events = asyncio.run(manager.get_events_for_ticket("550e8400-e29b-41d4-a716-446655440000"))

        assert len(events) == 0
