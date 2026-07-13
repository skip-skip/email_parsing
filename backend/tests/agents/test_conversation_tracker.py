from __future__ import annotations

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

from backend.app.agents.conversation_tracker import (
    ConversationTracker,
)
from backend.app.agents.merge_result import MergeResult
from shared.schemas.email import ParsedEmail


class TestConversationTracker:
    """Tests for ConversationTracker with mocked parsing agent and database."""

    TICKET_ID = "550e8400-e29b-41d4-a716-446655440000"
    CONVERSATION_ID = "conv-789"

    def _make_ticket_mock(
        self,
        client: str | None = None,
        project_number: str | None = None,
        task_description: str | None = None,
        deadline: datetime | None = None,
        budget_hours: float | None = None,
    ) -> MagicMock:
        ticket = MagicMock()
        ticket.client = client
        ticket.project_number = project_number
        ticket.task_description = task_description
        ticket.deadline = deadline
        ticket.budget_hours = budget_hours
        return ticket

    def _make_parsed_email(
        self,
        client: str | None = None,
        project_number: str | None = None,
        task_description: str | None = None,
        deadline: datetime | None = None,
        budget_hours: float | None = None,
        confidence: float = 0.9,
    ) -> ParsedEmail:
        return ParsedEmail(
            client=client,
            sender="test@example.com",
            subject="Test",
            project_number=project_number,
            task_description=task_description,
            deadline=deadline,
            budget_hours=budget_hours,
            confidence=confidence,
        )

    @patch("backend.app.agents.conversation_tracker.async_session_factory")
    async def test_field_merge_new_value(
        self, mock_session_factory: MagicMock
    ) -> None:
        """When a ticket field is None and the parsed email has a value, the field is updated."""
        mock_session = AsyncMock()
        mock_session_factory.return_value.__aenter__.return_value = mock_session

        ticket = self._make_ticket_mock(
            client=None,
            project_number=None,
        )

        mock_ticket_repo = MagicMock()
        mock_ticket_repo.get_by_id = AsyncMock(return_value=ticket)

        parsed = self._make_parsed_email(
            client="Acme Corp",
            project_number="PRJ-001",
        )

        mock_parsing_agent = MagicMock()
        mock_parsing_agent.parse = AsyncMock(return_value=parsed)

        with (
            patch(
                "backend.app.agents.conversation_tracker.TicketRepository",
                return_value=mock_ticket_repo,
            ),
            patch(
                "backend.app.agents.conversation_tracker.EmailParsingAgent",
                return_value=mock_parsing_agent,
            ),
        ):
            tracker = ConversationTracker(parsing_agent=mock_parsing_agent)
            result = await tracker.merge(
                ticket_id=self.TICKET_ID,
                new_email=MagicMock(),
                previous_emails=[],
            )

        assert ticket.client == "Acme Corp"
        assert ticket.project_number == "PRJ-001"
        assert "client" in result.updated_fields
        assert "project_number" in result.updated_fields

    @patch("backend.app.agents.conversation_tracker.async_session_factory")
    async def test_field_merge_different_value(
        self, mock_session_factory: MagicMock
    ) -> None:
        """When a ticket field has an old value and parsed has a different value, the field is updated."""
        mock_session = AsyncMock()
        mock_session_factory.return_value.__aenter__.return_value = mock_session

        ticket = self._make_ticket_mock(
            client="Old Corp",
            task_description="Old task description",
        )

        mock_ticket_repo = MagicMock()
        mock_ticket_repo.get_by_id = AsyncMock(return_value=ticket)

        parsed = self._make_parsed_email(
            client="New Corp",
            task_description="New task description",
        )

        mock_parsing_agent = MagicMock()
        mock_parsing_agent.parse = AsyncMock(return_value=parsed)

        with (
            patch(
                "backend.app.agents.conversation_tracker.TicketRepository",
                return_value=mock_ticket_repo,
            ),
            patch(
                "backend.app.agents.conversation_tracker.EmailParsingAgent",
                return_value=mock_parsing_agent,
            ),
        ):
            tracker = ConversationTracker(parsing_agent=mock_parsing_agent)
            result = await tracker.merge(
                ticket_id=self.TICKET_ID,
                new_email=MagicMock(),
                previous_emails=[],
            )

        assert ticket.client == "New Corp"
        assert ticket.task_description == "New task description"
        assert "client" in result.updated_fields
        assert "task_description" in result.updated_fields

    @patch("backend.app.agents.conversation_tracker.async_session_factory")
    async def test_field_merge_same_value(
        self, mock_session_factory: MagicMock
    ) -> None:
        """When a ticket field already has the same value as parsed, no update occurs."""
        deadline = datetime(2025, 7, 15, 0, 0, 0)

        mock_session = AsyncMock()
        mock_session_factory.return_value.__aenter__.return_value = mock_session

        ticket = self._make_ticket_mock(
            client="Acme Corp",
            task_description="Same description",
            deadline=deadline,
            budget_hours=20.0,
        )

        mock_ticket_repo = MagicMock()
        mock_ticket_repo.get_by_id = AsyncMock(return_value=ticket)

        parsed = self._make_parsed_email(
            client="Acme Corp",
            task_description="Same description",
            deadline=deadline,
            budget_hours=20.0,
        )

        mock_parsing_agent = MagicMock()
        mock_parsing_agent.parse = AsyncMock(return_value=parsed)

        with (
            patch(
                "backend.app.agents.conversation_tracker.TicketRepository",
                return_value=mock_ticket_repo,
            ),
            patch(
                "backend.app.agents.conversation_tracker.EmailParsingAgent",
                return_value=mock_parsing_agent,
            ),
        ):
            tracker = ConversationTracker(parsing_agent=mock_parsing_agent)
            result = await tracker.merge(
                ticket_id=self.TICKET_ID,
                new_email=MagicMock(),
                previous_emails=[],
            )

        # All fields are the same, so no updates should be recorded
        assert result.updated_fields == []

    @patch("backend.app.agents.conversation_tracker.async_session_factory")
    async def test_merge_result_tracks_changes(
        self, mock_session_factory: MagicMock
    ) -> None:
        """MergeResult should correctly report updated_fields, previous_values, and new_values."""
        mock_session = AsyncMock()
        mock_session_factory.return_value.__aenter__.return_value = mock_session

        ticket = self._make_ticket_mock(
            client="Old Client",
            project_number=None,
            task_description="Old desc",
        )

        mock_ticket_repo = MagicMock()
        mock_ticket_repo.get_by_id = AsyncMock(return_value=ticket)

        parsed = self._make_parsed_email(
            client="New Client",
            project_number="PRJ-999",
            task_description="Updated desc",
        )

        mock_parsing_agent = MagicMock()
        mock_parsing_agent.parse = AsyncMock(return_value=parsed)

        with (
            patch(
                "backend.app.agents.conversation_tracker.TicketRepository",
                return_value=mock_ticket_repo,
            ),
            patch(
                "backend.app.agents.conversation_tracker.EmailParsingAgent",
                return_value=mock_parsing_agent,
            ),
        ):
            tracker = ConversationTracker(parsing_agent=mock_parsing_agent)
            result = await tracker.merge(
                ticket_id=self.TICKET_ID,
                new_email=MagicMock(),
                previous_emails=[],
            )

        assert "client" in result.updated_fields
        assert result.previous_values["client"] == "Old Client"
        assert result.new_values["client"] == "New Client"

        assert "project_number" in result.updated_fields
        assert result.previous_values["project_number"] is None
        assert result.new_values["project_number"] == "PRJ-999"

        assert "task_description" in result.updated_fields
        assert result.previous_values["task_description"] == "Old desc"
        assert result.new_values["task_description"] == "Updated desc"

    @patch("backend.app.agents.conversation_tracker.async_session_factory")
    async def test_ticket_not_found(
        self, mock_session_factory: MagicMock
    ) -> None:
        """When the ticket is not found in the database, return an empty MergeResult."""
        mock_session = AsyncMock()
        mock_session_factory.return_value.__aenter__.return_value = mock_session

        mock_ticket_repo = MagicMock()
        mock_ticket_repo.get_by_id = AsyncMock(return_value=None)

        mock_parsing_agent = MagicMock()
        mock_parsing_agent.parse = AsyncMock(
            return_value=self._make_parsed_email(client="Should Not Apply")
        )

        with (
            patch(
                "backend.app.agents.conversation_tracker.TicketRepository",
                return_value=mock_ticket_repo,
            ),
            patch(
                "backend.app.agents.conversation_tracker.EmailParsingAgent",
                return_value=mock_parsing_agent,
            ),
        ):
            tracker = ConversationTracker(parsing_agent=mock_parsing_agent)
            result = await tracker.merge(
                ticket_id=self.TICKET_ID,
                new_email=MagicMock(),
                previous_emails=[],
            )

        assert isinstance(result, MergeResult)
        assert result.updated_fields == []
        assert result.previous_values == {}
        assert result.new_values == {}
