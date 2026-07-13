from __future__ import annotations

import asyncio
import uuid
from unittest.mock import AsyncMock, MagicMock, patch

from backend.app.agents.email_classification_agent import ClassificationResult
from backend.app.services.email_processor import EmailProcessor, ProcessingResult
from backend.app.services.outlook.models import EmailMessage


class TestEmailProcessor:
    """Tests for EmailProcessor with mocked dependencies."""

    def _make_message(
        self,
        sender: str = "bob@example.com",
        subject: str = "Website redesign",
        body: str = "Please redesign the company website.",
        entry_id: str = "entry-001",
        conversation_id: str = "conv-001",
    ) -> EmailMessage:
        return EmailMessage(
            conversation_id=conversation_id,
            entry_id=entry_id,
            sender=sender,
            subject=subject,
            body=body,
            received_time=None,
        )

    @patch("backend.app.services.email_processor.compile_workflow")
    @patch("backend.app.services.email_processor.async_session_factory")
    @patch("backend.app.services.email_processor.EmailClassificationAgent")
    def test_task_email_creates_ticket_and_invokes_workflow(
        self,
        mock_classifier_cls: MagicMock,
        mock_session_factory: MagicMock,
        mock_compile_workflow: MagicMock,
    ) -> None:
        """A task email should create a ticket and invoke the workflow."""
        mock_classifier = MagicMock()
        mock_classifier.classify = AsyncMock(
            return_value=ClassificationResult(
                is_task=True,
                category="task_request",
                confidence=0.95,
                reason="Client requesting work",
            )
        )
        mock_classifier_cls.return_value = mock_classifier

        ticket_id = uuid.uuid4()
        mock_ticket_repo = MagicMock()
        mock_ticket_repo.create = AsyncMock(
            return_value=MagicMock(ticket_id=ticket_id)
        )

        mock_email_repo = MagicMock()
        mock_email = MagicMock()
        mock_email_repo.get_by_entry_id = AsyncMock(return_value=mock_email)

        mock_session = AsyncMock()
        mock_session_factory.return_value.__aenter__.return_value = mock_session

        with patch(
            "backend.app.services.email_processor.TicketRepository",
            return_value=mock_ticket_repo,
        ), patch(
            "backend.app.services.email_processor.EmailRepository",
            return_value=mock_email_repo,
        ):
            mock_wf = MagicMock()
            mock_wf.invoke.return_value = {"status": "IN_PROGRESS"}
            mock_compile_workflow.return_value = mock_wf

            processor = EmailProcessor(classification_agent=mock_classifier)
            message = self._make_message()
            result = asyncio.run(processor.process_new_email(message))

        assert result.is_task is True
        assert result.ticket_id == str(ticket_id)
        assert result.workflow_status == "IN_PROGRESS"
        assert result.error is None

        mock_ticket_repo.create.assert_awaited_once()
        assert mock_email.ticket_id == ticket_id

    @patch("backend.app.services.email_processor.async_session_factory")
    @patch("backend.app.services.email_processor.EmailClassificationAgent")
    def test_non_task_email_skips_ticket_creation(
        self,
        mock_classifier_cls: MagicMock,
        mock_session_factory: MagicMock,
    ) -> None:
        """A non-task email should not create a ticket."""
        mock_classifier = MagicMock()
        mock_classifier.classify = AsyncMock(
            return_value=ClassificationResult(
                is_task=False,
                category="newsletter",
                confidence=0.92,
                reason="Marketing newsletter",
            )
        )
        mock_classifier_cls.return_value = mock_classifier

        mock_session = AsyncMock()
        mock_session_factory.return_value.__aenter__.return_value = mock_session

        processor = EmailProcessor(classification_agent=mock_classifier)
        message = self._make_message()
        result = asyncio.run(processor.process_new_email(message))

        assert result.is_task is False
        assert result.ticket_id is None
        assert result.workflow_status is None
        assert result.error is None

    @patch("backend.app.services.email_processor.async_session_factory")
    @patch("backend.app.services.email_processor.EmailClassificationAgent")
    def test_classification_failure_fails_open(
        self,
        mock_classifier_cls: MagicMock,
        mock_session_factory: MagicMock,
    ) -> None:
        """When classification fails, should fail-open and process as task."""
        mock_classifier = MagicMock()
        mock_classifier.classify = AsyncMock(
            return_value=ClassificationResult(
                is_task=True,
                category="other",
                confidence=0.0,
                reason="Classification failed, defaulting to task (fail-open)",
            )
        )
        mock_classifier_cls.return_value = mock_classifier

        ticket_id = uuid.uuid4()
        mock_ticket_repo = MagicMock()
        mock_ticket_repo.create = AsyncMock(
            return_value=MagicMock(ticket_id=ticket_id)
        )

        mock_email_repo = MagicMock()
        mock_email = MagicMock()
        mock_email_repo.get_by_entry_id = AsyncMock(return_value=mock_email)

        mock_session = AsyncMock()
        mock_session_factory.return_value.__aenter__.return_value = mock_session

        with patch(
            "backend.app.services.email_processor.TicketRepository",
            return_value=mock_ticket_repo,
        ), patch(
            "backend.app.services.email_processor.EmailRepository",
            return_value=mock_email_repo,
        ), patch(
            "backend.app.services.email_processor.compile_workflow"
        ) as mock_compile:
            mock_wf = MagicMock()
            mock_wf.invoke.return_value = {"status": "IN_PROGRESS"}
            mock_compile.return_value = mock_wf

            processor = EmailProcessor(classification_agent=mock_classifier)
            message = self._make_message()
            result = asyncio.run(processor.process_new_email(message))

        assert result.is_task is True
        assert result.ticket_id is not None

    @patch("backend.app.services.email_processor.async_session_factory")
    @patch("backend.app.services.email_processor.EmailClassificationAgent")
    def test_ticket_creation_failure_returns_error(
        self,
        mock_classifier_cls: MagicMock,
        mock_session_factory: MagicMock,
    ) -> None:
        """When ticket creation fails, should return an error."""
        mock_classifier = MagicMock()
        mock_classifier.classify = AsyncMock(
            return_value=ClassificationResult(
                is_task=True,
                category="task_request",
                confidence=0.9,
                reason="Task request",
            )
        )
        mock_classifier_cls.return_value = mock_classifier

        mock_ticket_repo = MagicMock()
        mock_ticket_repo.create = AsyncMock(
            side_effect=Exception("DB connection lost")
        )

        mock_session = AsyncMock()
        mock_session_factory.return_value.__aenter__.return_value = mock_session

        with patch(
            "backend.app.services.email_processor.TicketRepository",
            return_value=mock_ticket_repo,
        ):
            processor = EmailProcessor(classification_agent=mock_classifier)
            message = self._make_message()
            result = asyncio.run(processor.process_new_email(message))

        assert result.is_task is True
        assert result.ticket_id is None
        assert result.error is not None

    @patch("backend.app.services.email_processor.compile_workflow")
    @patch("backend.app.services.email_processor.async_session_factory")
    @patch("backend.app.services.email_processor.EmailClassificationAgent")
    def test_workflow_failure_returns_error(
        self,
        mock_classifier_cls: MagicMock,
        mock_session_factory: MagicMock,
        mock_compile_workflow: MagicMock,
    ) -> None:
        """When workflow invocation fails, should return an error."""
        mock_classifier = MagicMock()
        mock_classifier.classify = AsyncMock(
            return_value=ClassificationResult(
                is_task=True,
                category="task_request",
                confidence=0.9,
                reason="Task request",
            )
        )
        mock_classifier_cls.return_value = mock_classifier

        ticket_id = uuid.uuid4()
        mock_ticket_repo = MagicMock()
        mock_ticket_repo.create = AsyncMock(
            return_value=MagicMock(ticket_id=ticket_id)
        )

        mock_email_repo = MagicMock()
        mock_email = MagicMock()
        mock_email_repo.get_by_entry_id = AsyncMock(return_value=mock_email)

        mock_session = AsyncMock()
        mock_session_factory.return_value.__aenter__.return_value = mock_session

        mock_wf = MagicMock()
        mock_wf.invoke.side_effect = Exception("Workflow crashed")
        mock_compile_workflow.return_value = mock_wf

        with patch(
            "backend.app.services.email_processor.TicketRepository",
            return_value=mock_ticket_repo,
        ), patch(
            "backend.app.services.email_processor.EmailRepository",
            return_value=mock_email_repo,
        ):
            processor = EmailProcessor(classification_agent=mock_classifier)
            message = self._make_message()
            result = asyncio.run(processor.process_new_email(message))

        assert result.is_task is True
        assert result.ticket_id is not None
        assert result.error is not None

    @patch("backend.app.services.email_processor.async_session_factory")
    @patch("backend.app.services.email_processor.EmailClassificationAgent")
    def test_returns_correct_entry_id(
        self,
        mock_classifier_cls: MagicMock,
        mock_session_factory: MagicMock,
    ) -> None:
        """ProcessingResult should contain the original entry_id."""
        mock_classifier = MagicMock()
        mock_classifier.classify = AsyncMock(
            return_value=ClassificationResult(
                is_task=False,
                category="spam",
                confidence=0.88,
                reason="Spam email",
            )
        )
        mock_classifier_cls.return_value = mock_classifier

        mock_session = AsyncMock()
        mock_session_factory.return_value.__aenter__.return_value = mock_session

        processor = EmailProcessor(classification_agent=mock_classifier)
        message = self._make_message(entry_id="unique-entry-123")
        result = asyncio.run(processor.process_new_email(message))

        assert result.entry_id == "unique-entry-123"
