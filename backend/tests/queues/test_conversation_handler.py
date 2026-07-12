from __future__ import annotations

import asyncio
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from backend.app.services.conversation_handler import ConversationHandler, ReplyResult
from shared.schemas.email import EmailMessage


class TestConversationHandler:
    def _make_reply(self) -> EmailMessage:
        return EmailMessage(
            email_id="550e8400-e29b-41d4-a716-446655440001",
            conversation_id="conv-123",
            entry_id="entry-456",
            sender="bob@example.com",
            subject="Re: Website redesign",
            body="Project number is PRJ-2025-001 and deadline is 2025-12-31",
            received_time=datetime(2025, 6, 15, 10, 0, 0),
            attachments=[],
        )

    @patch("backend.app.services.conversation_handler.async_session_factory")
    @patch("backend.app.services.conversation_handler.ConversationTracker")
    @patch("backend.app.services.conversation_handler.TicketValidator")
    def test_reply_merges_information(
        self, mock_validator_cls: MagicMock, mock_tracker_cls: MagicMock, mock_session_factory: MagicMock
    ) -> None:
        mock_ticket = MagicMock()
        mock_ticket.ticket_id = "550e8400-e29b-41d4-a716-446655440000"
        mock_ticket.status = "WAITING_FOR_INFORMATION"
        mock_ticket.task_description = "Redesign website"
        mock_ticket.project_number = None
        mock_ticket.budget_hours = None
        mock_ticket.deadline = None

        mock_session = AsyncMock()
        mock_session_factory.return_value.__aenter__.return_value = mock_session

        mock_ticket_repo = MagicMock()
        mock_ticket_repo.get_by_conversation_id = AsyncMock(return_value=mock_ticket)

        mock_email_repo = MagicMock()
        mock_email_repo.get_by_conversation_id = AsyncMock(return_value=[])

        mock_tracker = MagicMock()
        mock_merge_result = MagicMock()
        mock_merge_result.updated_fields = ["project_number", "deadline"]
        mock_merge_result.new_values = {"project_number": "PRJ-2025-001", "deadline": "2025-12-31"}
        mock_tracker.merge = AsyncMock(return_value=mock_merge_result)
        mock_tracker_cls.return_value = mock_tracker

        mock_validator = MagicMock()
        mock_validation_result = MagicMock()
        mock_validation_result.is_complete = True
        mock_validation_result.missing_fields = []
        mock_validator.validate.return_value = mock_validation_result
        mock_validator_cls.return_value = mock_validator

        with (
            patch("backend.app.services.conversation_handler.TicketRepository", return_value=mock_ticket_repo),
            patch("backend.app.services.conversation_handler.EmailRepository", return_value=mock_email_repo),
            patch("backend.app.services.conversation_handler.transition_ticket", new_callable=AsyncMock),
        ):
            handler = ConversationHandler(tracker=mock_tracker, validator=mock_validator)
            result = asyncio.run(handler.handle_reply("conv-123", self._make_reply()))

        assert result is not None
        assert result.is_complete is True
        assert "project_number" in result.updated_fields
