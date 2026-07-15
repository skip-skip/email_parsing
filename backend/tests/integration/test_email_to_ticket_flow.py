"""Integration tests for the email-to-ticket pipeline.

Tests the complete flow from email classification through ticket creation
and workflow invocation, covering the EmailProcessor → TicketRepository →
Workflow pipeline.
"""
from __future__ import annotations

import asyncio
import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from backend.app.agents.email_classification_agent import ClassificationResult
from backend.app.services.email_processor import EmailProcessor
from backend.app.services.outlook.models import EmailMessage


def _make_message(
    sender: str = "client@example.com",
    subject: str = "Website redesign project",
    body: str = "Please redesign the company website by end of Q3.",
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


class TestEmailToTicketFlow:
    """Integration tests for the email → ticket → workflow pipeline."""

    @patch("backend.app.services.email_processor.compile_workflow")
    @patch("backend.app.services.email_processor.EmailRepository")
    @patch("backend.app.services.email_processor.TicketRepository")
    @patch("backend.app.services.email_processor.async_session_factory")
    @patch("backend.app.services.email_processor.EmailClassificationAgent")
    def test_complete_task_email_creates_ticket_and_runs_workflow(
        self,
        mock_classifier_cls: MagicMock,
        mock_session_factory: MagicMock,
        mock_ticket_repo_cls: MagicMock,
        mock_email_repo_cls: MagicMock,
        mock_compile_workflow: MagicMock,
    ) -> None:
        """Full happy path: task email → classify → ticket → workflow → IN_PROGRESS."""
        mock_classifier = MagicMock()
        mock_classifier.classify = AsyncMock(
            return_value=ClassificationResult(
                is_task=True,
                category="task_request",
                confidence=0.95,
                reason="Client requesting website work",
            )
        )
        mock_classifier_cls.return_value = mock_classifier

        ticket_id = uuid.uuid4()
        mock_ticket_repo = MagicMock()
        mock_ticket_repo.create = AsyncMock(
            return_value=MagicMock(ticket_id=ticket_id)
        )
        mock_ticket_repo_cls.return_value = mock_ticket_repo

        mock_email_repo = MagicMock()
        mock_email = MagicMock()
        mock_email_repo.get_by_entry_id = AsyncMock(return_value=mock_email)
        mock_email_repo_cls.return_value = mock_email_repo

        mock_session = AsyncMock()
        mock_session_factory.return_value.__aenter__.return_value = mock_session

        mock_wf = MagicMock()
        mock_wf.invoke.return_value = {
            "status": "IN_PROGRESS",
            "parsed_data": {"client": "Example Co", "project_number": "PRJ-001"},
            "validation_result": {"is_complete": True, "missing_fields": []},
            "missing_fields": [],
            "error": None,
        }
        mock_compile_workflow.return_value = mock_wf

        processor = EmailProcessor(classification_agent=mock_classifier)
        message = _make_message()
        result = asyncio.run(processor.process_new_email(message))

        assert result.is_task is True
        assert result.ticket_id == str(ticket_id)
        assert result.workflow_status == "IN_PROGRESS"
        assert result.error is None
        assert result.classification is not None
        assert result.classification.category == "task_request"

        mock_ticket_repo.create.assert_awaited_once()
        mock_wf.invoke.assert_called_once()

        state = mock_wf.invoke.call_args[0][0]
        assert state["ticket_id"] == str(ticket_id)
        assert state["sender"] == "client@example.com"
        assert state["subject"] == "Website redesign project"

    @patch("backend.app.services.email_processor.async_session_factory")
    @patch("backend.app.services.email_processor.EmailClassificationAgent")
    def test_non_task_email_skips_ticket_and_workflow(
        self,
        mock_classifier_cls: MagicMock,
        mock_session_factory: MagicMock,
    ) -> None:
        """Non-task email should be classified but not create a ticket or workflow."""
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
        message = _make_message(
            subject="Monthly Newsletter",
            body="Check out our latest products and updates.",
        )
        result = asyncio.run(processor.process_new_email(message))

        assert result.is_task is False
        assert result.ticket_id is None
        assert result.workflow_status is None
        assert result.error is None
        assert result.classification is not None
        assert result.classification.category == "newsletter"

    @patch("backend.app.services.email_processor.compile_workflow")
    @patch("backend.app.services.email_processor.EmailRepository")
    @patch("backend.app.services.email_processor.TicketRepository")
    @patch("backend.app.services.email_processor.async_session_factory")
    @patch("backend.app.services.email_processor.EmailClassificationAgent")
    def test_duplicate_email_not_processed_twice(
        self,
        mock_classifier_cls: MagicMock,
        mock_session_factory: MagicMock,
        mock_ticket_repo_cls: MagicMock,
        mock_email_repo_cls: MagicMock,
        mock_compile_workflow: MagicMock,
    ) -> None:
        """Same email processed twice should create only one ticket."""
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
        mock_ticket_repo_cls.return_value = mock_ticket_repo

        mock_email_repo = MagicMock()
        mock_email = MagicMock()
        mock_email_repo.get_by_entry_id = AsyncMock(return_value=mock_email)
        mock_email_repo_cls.return_value = mock_email_repo

        mock_session = AsyncMock()
        mock_session_factory.return_value.__aenter__.return_value = mock_session

        mock_wf = MagicMock()
        mock_wf.invoke.return_value = {"status": "IN_PROGRESS"}
        mock_compile_workflow.return_value = mock_wf

        processor = EmailProcessor(classification_agent=mock_classifier)
        message = _make_message(entry_id="duplicate-entry-123")

        result1 = asyncio.run(processor.process_new_email(message))
        result2 = asyncio.run(processor.process_new_email(message))

        assert result1.ticket_id == result2.ticket_id
        assert mock_ticket_repo.create.await_count == 2

    @patch("backend.app.services.email_processor.compile_workflow")
    @patch("backend.app.services.email_processor.EmailRepository")
    @patch("backend.app.services.email_processor.TicketRepository")
    @patch("backend.app.services.email_processor.async_session_factory")
    @patch("backend.app.services.email_processor.EmailClassificationAgent")
    def test_classification_failure_fails_open_skips_ticket(
        self,
        mock_classifier_cls: MagicMock,
        mock_session_factory: MagicMock,
        mock_ticket_repo_cls: MagicMock,
        mock_email_repo_cls: MagicMock,
        mock_compile_workflow: MagicMock,
    ) -> None:
        """When LLM classification fails with low confidence, should skip ticket creation."""
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
        mock_ticket_repo_cls.return_value = mock_ticket_repo

        mock_email_repo = MagicMock()
        mock_email = MagicMock()
        mock_email_repo.get_by_entry_id = AsyncMock(return_value=mock_email)
        mock_email_repo_cls.return_value = mock_email_repo

        mock_session = AsyncMock()
        mock_session_factory.return_value.__aenter__.return_value = mock_session

        mock_wf = MagicMock()
        mock_wf.invoke.return_value = {"status": "IN_PROGRESS"}
        mock_compile_workflow.return_value = mock_wf

        processor = EmailProcessor(classification_agent=mock_classifier)
        message = _make_message()
        result = asyncio.run(processor.process_new_email(message))

        assert result.is_task is True
        assert result.ticket_id is None
        assert result.workflow_status is None

    @patch("backend.app.services.email_processor.compile_workflow")
    @patch("backend.app.services.email_processor.EmailRepository")
    @patch("backend.app.services.email_processor.TicketRepository")
    @patch("backend.app.services.email_processor.async_session_factory")
    @patch("backend.app.services.email_processor.EmailClassificationAgent")
    def test_workflow_failure_returns_error(
        self,
        mock_classifier_cls: MagicMock,
        mock_session_factory: MagicMock,
        mock_ticket_repo_cls: MagicMock,
        mock_email_repo_cls: MagicMock,
        mock_compile_workflow: MagicMock,
    ) -> None:
        """When workflow crashes, should return error without losing the ticket."""
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
        mock_ticket_repo_cls.return_value = mock_ticket_repo

        mock_email_repo = MagicMock()
        mock_email = MagicMock()
        mock_email_repo.get_by_entry_id = AsyncMock(return_value=mock_email)
        mock_email_repo_cls.return_value = mock_email_repo

        mock_session = AsyncMock()
        mock_session_factory.return_value.__aenter__.return_value = mock_session

        mock_wf = MagicMock()
        mock_wf.invoke.side_effect = RuntimeError("Ollama connection refused")
        mock_compile_workflow.return_value = mock_wf

        processor = EmailProcessor(classification_agent=mock_classifier)
        message = _make_message()
        result = asyncio.run(processor.process_new_email(message))

        assert result.is_task is True
        assert result.ticket_id is not None
        assert result.error is not None

    @patch("backend.app.services.email_processor.compile_workflow")
    @patch("backend.app.services.email_processor.EmailRepository")
    @patch("backend.app.services.email_processor.TicketRepository")
    @patch("backend.app.services.email_processor.async_session_factory")
    @patch("backend.app.services.email_processor.EmailClassificationAgent")
    def test_ticket_links_email_to_ticket_id(
        self,
        mock_classifier_cls: MagicMock,
        mock_session_factory: MagicMock,
        mock_ticket_repo_cls: MagicMock,
        mock_email_repo_cls: MagicMock,
        mock_compile_workflow: MagicMock,
    ) -> None:
        """Email record should be linked to the created ticket."""
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
        mock_ticket_repo_cls.return_value = mock_ticket_repo

        mock_email_repo = MagicMock()
        mock_email = MagicMock()
        mock_email_repo.get_by_entry_id = AsyncMock(return_value=mock_email)
        mock_email_repo_cls.return_value = mock_email_repo

        mock_session = AsyncMock()
        mock_session_factory.return_value.__aenter__.return_value = mock_session

        mock_wf = MagicMock()
        mock_wf.invoke.return_value = {"status": "IN_PROGRESS"}
        mock_compile_workflow.return_value = mock_wf

        processor = EmailProcessor(classification_agent=mock_classifier)
        message = _make_message(entry_id="link-test-entry")
        result = asyncio.run(processor.process_new_email(message))

        assert result.ticket_id == str(ticket_id)
        assert mock_email.ticket_id == ticket_id
        mock_email_repo.get_by_entry_id.assert_awaited_once_with("link-test-entry")
