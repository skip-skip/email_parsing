from __future__ import annotations

import asyncio
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

from backend.app.agents.calendar_planning_agent import (
    CalendarPlanningAgent,
    ScheduleSuggestion,
)


class TestCalendarPlanningAgent:
    @patch("backend.app.agents.calendar_planning_agent.async_session_factory")
    def test_suggest_schedule(self, mock_session_factory: MagicMock) -> None:
        mock_session = AsyncMock()
        mock_session_factory.return_value.__aenter__.return_value = mock_session

        with patch("backend.app.agents.calendar_planning_agent.AILogRepository", return_value=MagicMock()):
            agent = CalendarPlanningAgent()
            deadline = datetime.now() + timedelta(days=7)
            result = asyncio.run(
                agent.suggest_schedule(
                    ticket_id="550e8400-e29b-41d4-a716-446655440000",
                    deadline=deadline,
                    budget_hours=20,
                    task_description="Redesign website",
                )
            )

        assert isinstance(result, ScheduleSuggestion)
        assert result.total_hours > 0
        assert len(result.blocks) > 0

    @patch("backend.app.agents.calendar_planning_agent.async_session_factory")
    def test_past_deadline_returns_empty(self, mock_session_factory: MagicMock) -> None:
        mock_session = AsyncMock()
        mock_session_factory.return_value.__aenter__.return_value = mock_session

        with patch("backend.app.agents.calendar_planning_agent.AILogRepository", return_value=MagicMock()):
            agent = CalendarPlanningAgent()
            deadline = datetime.now() - timedelta(days=1)
            result = asyncio.run(
                agent.suggest_schedule(
                    ticket_id="550e8400-e29b-41d4-a716-446655440000",
                    deadline=deadline,
                    budget_hours=20,
                    task_description="Redesign website",
                )
            )

        assert result.fits_deadline is False
        assert len(result.blocks) == 0
