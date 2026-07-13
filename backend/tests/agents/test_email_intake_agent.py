from __future__ import annotations

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

from backend.app.agents.email_intake_agent import EmailIntakeAgent, IntakeResponse
from backend.app.services.outlook.models import EmailMessage


class TestEmailIntakeAgent:
    def _make_message(
        self,
        conversation_id: str = "conv-123",
        entry_id: str = "entry-456",
    ) -> EmailMessage:
        return EmailMessage(
            conversation_id=conversation_id,
            entry_id=entry_id,
            sender="alice@example.com",
            subject="Test Subject",
            body="Test body",
            received_time=datetime(2025, 6, 1, 12, 0, 0),
            attachments=[],
        )

    @patch("backend.app.agents.email_intake_agent.async_session_factory")
    async def test_new_email_is_stored(self, mock_session_factory: MagicMock) -> None:
        """A brand-new email should be stored and return ready_for_parsing=True."""
        message = self._make_message()

        # Mock session context manager
        mock_session = AsyncMock()
        mock_session_factory.return_value.__aenter__.return_value = mock_session

        # Mock email repository
        mock_email_repo = MagicMock()
        mock_email_repo.get_by_entry_id = AsyncMock(return_value=None)

        mock_created_email = MagicMock()
        mock_created_email.email_id = "uuid-email-1"
        mock_email_repo.create = AsyncMock(return_value=mock_created_email)

        # Mock ticket repository
        mock_ticket_repo = MagicMock()
        mock_ticket_repo.get_by_conversation_id = AsyncMock(return_value=None)

        # Patch repository constructors
        with (
            patch(
                "backend.app.agents.email_intake_agent.EmailRepository",
                return_value=mock_email_repo,
            ),
            patch(
                "backend.app.agents.email_intake_agent.TicketRepository",
                return_value=mock_ticket_repo,
            ),
        ):
            agent = EmailIntakeAgent()
            result = await agent.process(message)

        assert isinstance(result, IntakeResponse)
        assert result.email_id == "uuid-email-1"
        assert result.is_new_thread is True
        assert result.existing_ticket_id is None
        assert result.ready_for_parsing is True

        mock_email_repo.create.assert_awaited_once()
        mock_session.commit.assert_awaited_once()

    @patch("backend.app.agents.email_intake_agent.async_session_factory")
    async def test_duplicate_detection(self, mock_session_factory: MagicMock) -> None:
        """An email with an existing entry_id should return ready_for_parsing=False."""
        message = self._make_message()

        mock_session = AsyncMock()
        mock_session_factory.return_value.__aenter__.return_value = mock_session

        mock_existing_email = MagicMock()
        mock_existing_email.email_id = "uuid-existing"
        mock_existing_email.ticket_id = None

        mock_email_repo = MagicMock()
        mock_email_repo.get_by_entry_id = AsyncMock(return_value=mock_existing_email)

        with (
            patch(
                "backend.app.agents.email_intake_agent.EmailRepository",
                return_value=mock_email_repo,
            ),
            patch(
                "backend.app.agents.email_intake_agent.TicketRepository",
                return_value=MagicMock(),
            ),
        ):
            agent = EmailIntakeAgent()
            result = await agent.process(message)

        assert result.ready_for_parsing is False
        assert result.is_new_thread is False
        assert result.email_id == "uuid-existing"

    @patch("backend.app.agents.email_intake_agent.async_session_factory")
    async def test_conversation_linking(
        self, mock_session_factory: MagicMock
    ) -> None:
        """An email matching an existing conversation should link and set is_new_thread=False."""
        message = self._make_message(conversation_id="conv-existing-ticket")

        mock_session = AsyncMock()
        mock_session_factory.return_value.__aenter__.return_value = mock_session

        mock_email_repo = MagicMock()
        mock_email_repo.get_by_entry_id = AsyncMock(return_value=None)
        mock_created_email = MagicMock()
        mock_created_email.email_id = "uuid-new"
        mock_email_repo.create = AsyncMock(return_value=mock_created_email)

        mock_existing_ticket = MagicMock()
        mock_existing_ticket.ticket_id = "uuid-ticket-1"

        mock_ticket_repo = MagicMock()
        mock_ticket_repo.get_by_conversation_id = AsyncMock(
            return_value=mock_existing_ticket
        )

        with (
            patch(
                "backend.app.agents.email_intake_agent.EmailRepository",
                return_value=mock_email_repo,
            ),
            patch(
                "backend.app.agents.email_intake_agent.TicketRepository",
                return_value=mock_ticket_repo,
            ),
        ):
            agent = EmailIntakeAgent()
            result = await agent.process(message)

        assert result.is_new_thread is False
        assert result.existing_ticket_id is None  # ticket_id not set on email here
        assert result.ready_for_parsing is True

        mock_ticket_repo.get_by_conversation_id.assert_awaited_once_with(
            "conv-existing-ticket"
        )
