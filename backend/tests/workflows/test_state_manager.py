from __future__ import annotations

import asyncio
import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from backend.app.workflows.states import TicketStatus
from backend.app.workflows.transitions import InvalidTransitionError
from backend.app.workflows.state_manager import transition_ticket


class TestTransitionTicket:
    """Tests for transition_ticket with strict_mode."""

    def _make_ticket(self, status: str = "NEW") -> MagicMock:
        ticket = MagicMock()
        ticket.ticket_id = uuid.uuid4()
        ticket.status = status
        return ticket

    @patch("backend.app.workflows.state_manager.async_session_factory")
    def test_valid_transition_updates_status(self, mock_session_factory: MagicMock) -> None:
        ticket = self._make_ticket("NEW")
        mock_ticket_repo = MagicMock()
        mock_ticket_repo.get_by_id = AsyncMock(return_value=ticket)
        mock_ticket_repo.update = AsyncMock(return_value=ticket)
        mock_log_repo = MagicMock()
        mock_log_repo.create = AsyncMock()

        mock_session = AsyncMock()
        mock_session_factory.return_value.__aenter__.return_value = mock_session

        with patch("backend.app.workflows.state_manager.TicketRepository", return_value=mock_ticket_repo), \
             patch("backend.app.workflows.state_manager.AILogRepository", return_value=mock_log_repo):
            result = asyncio.run(transition_ticket(ticket.ticket_id, TicketStatus.PARSED))

        mock_ticket_repo.update.assert_awaited_once_with(
            ticket.ticket_id, status=TicketStatus.PARSED.value
        )

    @patch("backend.app.workflows.state_manager.async_session_factory")
    def test_invalid_transition_raises_in_strict_mode(self, mock_session_factory: MagicMock) -> None:
        ticket = self._make_ticket("NEW")
        mock_ticket_repo = MagicMock()
        mock_ticket_repo.get_by_id = AsyncMock(return_value=ticket)
        mock_log_repo = MagicMock()

        mock_session = AsyncMock()
        mock_session_factory.return_value.__aenter__.return_value = mock_session

        with patch("backend.app.workflows.state_manager.TicketRepository", return_value=mock_ticket_repo), \
             patch("backend.app.workflows.state_manager.AILogRepository", return_value=mock_log_repo):
            with pytest.raises(InvalidTransitionError):
                asyncio.run(transition_ticket(ticket.ticket_id, TicketStatus.COMPLETED, strict_mode=True))

        mock_ticket_repo.update.assert_not_called()

    @patch("backend.app.workflows.state_manager.async_session_factory")
    def test_invalid_transition_allows_in_non_strict_mode(self, mock_session_factory: MagicMock) -> None:
        ticket = self._make_ticket("NEW")
        mock_ticket_repo = MagicMock()
        mock_ticket_repo.get_by_id = AsyncMock(return_value=ticket)
        mock_ticket_repo.update = AsyncMock(return_value=ticket)
        mock_log_repo = MagicMock()
        mock_log_repo.create = AsyncMock()

        mock_session = AsyncMock()
        mock_session_factory.return_value.__aenter__.return_value = mock_session

        with patch("backend.app.workflows.state_manager.TicketRepository", return_value=mock_ticket_repo), \
             patch("backend.app.workflows.state_manager.AILogRepository", return_value=mock_log_repo):
            result = asyncio.run(transition_ticket(ticket.ticket_id, TicketStatus.COMPLETED, strict_mode=False))

        mock_ticket_repo.update.assert_awaited_once_with(
            ticket.ticket_id, status=TicketStatus.COMPLETED.value
        )

    @patch("backend.app.workflows.state_manager.async_session_factory")
    def test_non_strict_is_default(self, mock_session_factory: MagicMock) -> None:
        ticket = self._make_ticket("NEW")
        mock_ticket_repo = MagicMock()
        mock_ticket_repo.get_by_id = AsyncMock(return_value=ticket)
        mock_ticket_repo.update = AsyncMock(return_value=ticket)
        mock_log_repo = MagicMock()
        mock_log_repo.create = AsyncMock()

        mock_session = AsyncMock()
        mock_session_factory.return_value.__aenter__.return_value = mock_session

        with patch("backend.app.workflows.state_manager.TicketRepository", return_value=mock_ticket_repo), \
             patch("backend.app.workflows.state_manager.AILogRepository", return_value=mock_log_repo):
            result = asyncio.run(transition_ticket(ticket.ticket_id, TicketStatus.COMPLETED))

        mock_ticket_repo.update.assert_awaited_once()

    @patch("backend.app.workflows.state_manager.async_session_factory")
    def test_ticket_not_found_raises_value_error(self, mock_session_factory: MagicMock) -> None:
        mock_ticket_repo = MagicMock()
        mock_ticket_repo.get_by_id = AsyncMock(return_value=None)
        mock_log_repo = MagicMock()

        mock_session = AsyncMock()
        mock_session_factory.return_value.__aenter__.return_value = mock_session

        with patch("backend.app.workflows.state_manager.TicketRepository", return_value=mock_ticket_repo), \
             patch("backend.app.workflows.state_manager.AILogRepository", return_value=mock_log_repo):
            with pytest.raises(ValueError, match="not found"):
                asyncio.run(transition_ticket(uuid.uuid4(), TicketStatus.PARSED))

    @patch("backend.app.workflows.state_manager.async_session_factory")
    def test_logs_transition_to_ai_log(self, mock_session_factory: MagicMock) -> None:
        ticket = self._make_ticket("NEW")
        mock_ticket_repo = MagicMock()
        mock_ticket_repo.get_by_id = AsyncMock(return_value=ticket)
        mock_ticket_repo.update = AsyncMock(return_value=ticket)
        mock_log_repo = MagicMock()
        mock_log_repo.create = AsyncMock()

        mock_session = AsyncMock()
        mock_session_factory.return_value.__aenter__.return_value = mock_session

        with patch("backend.app.workflows.state_manager.TicketRepository", return_value=mock_ticket_repo), \
             patch("backend.app.workflows.state_manager.AILogRepository", return_value=mock_log_repo):
            asyncio.run(transition_ticket(ticket.ticket_id, TicketStatus.PARSED))

        mock_log_repo.create.assert_awaited_once()
        call_kwargs = mock_log_repo.create.call_args.kwargs
        assert call_kwargs["parsed_json"]["previous_status"] == "NEW"
        assert call_kwargs["parsed_json"]["new_status"] == "PARSED"
