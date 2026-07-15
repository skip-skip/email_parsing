"""Email processor service — bridges Outlook monitor to LangGraph workflow.

Classifies incoming emails, creates tickets for task requests, and
invokes the workflow for automatic processing.
"""
from __future__ import annotations

import asyncio
import logging
import time
import uuid
from dataclasses import dataclass, field

from backend.app.agents.email_classification_agent import (
    ClassificationResult,
    EmailClassificationAgent,
)
from backend.app.agents.email_draft_agent import DraftEmail, EmailDraftAgent
from backend.app.services.database import async_session_factory
from backend.app.services.database.repositories.email_repository import (
    EmailRepository,
)
from backend.app.services.database.repositories.ticket_repository import (
    TicketRepository,
)
from backend.app.services.outlook.models import EmailMessage
from backend.app.services.queues.missing_info_queue import get_missing_info_queue
from backend.app.workflows.graph import compile_workflow
from backend.app.workflows.states import TicketStatus
from backend.app.workflows.state_manager import transition_ticket

logger = logging.getLogger(__name__)

DEFAULT_FAILURE_THRESHOLD = 3
DEFAULT_COOLDOWN_SECONDS = 300
MIN_TASK_CONFIDENCE = 0.5


class CircuitBreaker:
    """Circuit breaker that skips classification after consecutive failures.

    Opens after ``failure_threshold`` consecutive failures and stays open
    for ``cooldown_seconds``.  Closes again once the cooldown expires and
    the next attempt succeeds.
    """

    def __init__(
        self,
        failure_threshold: int = DEFAULT_FAILURE_THRESHOLD,
        cooldown_seconds: float = DEFAULT_COOLDOWN_SECONDS,
    ) -> None:
        self._failure_threshold = failure_threshold
        self._cooldown_seconds = cooldown_seconds
        self._consecutive_failures = 0
        self._last_failure_time: float | None = None
        self._is_open = False

    @property
    def is_open(self) -> bool:
        if not self._is_open:
            return False
        if self._last_failure_time is None:
            return False
        elapsed = time.monotonic() - self._last_failure_time
        if elapsed >= self._cooldown_seconds:
            logger.info(
                "Circuit breaker cooldown expired, allowing next attempt"
            )
            self._is_open = False
            return False
        return True

    def record_success(self) -> None:
        if self._consecutive_failures > 0 or self._is_open:
            logger.info(
                "Circuit breaker closed after %d consecutive failures",
                self._consecutive_failures,
            )
        self._consecutive_failures = 0
        self._is_open = False
        self._last_failure_time = None

    def record_failure(self) -> None:
        self._consecutive_failures += 1
        self._last_failure_time = time.monotonic()
        if self._consecutive_failures >= self._failure_threshold and not self._is_open:
            self._is_open = True
            logger.warning(
                "Circuit breaker opened after %d consecutive failures",
                self._consecutive_failures,
            )


@dataclass
class ProcessingResult:
    """Result of processing a single email through the pipeline."""

    entry_id: str
    ticket_id: str | None = None
    is_task: bool = False
    classification: ClassificationResult | None = None
    workflow_status: str | None = None
    error: str | None = None


class EmailProcessor:
    """Processes incoming emails through classification, ticket creation, and workflow.

    Acts as the bridge between the Outlook monitor and the LangGraph workflow.
    Each new email is classified by the LLM, and if it's a task request,
    a ticket is created and the workflow is invoked.
    """

    def __init__(
        self,
        classification_agent: EmailClassificationAgent | None = None,
        circuit_breaker: CircuitBreaker | None = None,
        conversation_handler: "ConversationHandler | None" = None,
    ) -> None:
        self._classifier = classification_agent or EmailClassificationAgent()
        self._circuit_breaker = circuit_breaker or CircuitBreaker()
        self._conversation_handler = conversation_handler

    async def process_new_email(self, message: EmailMessage) -> ProcessingResult:
        """Process a new email through the classification and workflow pipeline.

        If the email is a reply to an existing ticket awaiting information,
        it is routed to the ConversationHandler instead of being classified.

        Args:
            message: The incoming email message from Outlook.

        Returns:
            ProcessingResult with classification, ticket, and workflow status.
        """
        result = ProcessingResult(entry_id=message.entry_id)

        try:
            reply_result = await self._try_handle_reply(message)
            if reply_result is not None:
                result.ticket_id = reply_result.ticket_id
                result.is_task = True
                result.workflow_status = reply_result.status
                logger.info(
                    "Handled reply for ticket %s (fields updated: %s, complete: %s)",
                    reply_result.ticket_id,
                    reply_result.updated_fields,
                    reply_result.is_complete,
                )
                return result

            if self._circuit_breaker.is_open:
                logger.warning(
                    "Circuit breaker open — skipping classification for %s",
                    message.entry_id,
                )
                result.classification = self._classifier._fail_open_result(
                    message.sender, message.subject
                )
                result.is_task = False
                return result

            classification = await self._classifier.classify(
                sender=message.sender,
                subject=message.subject,
                body=message.body,
            )
            self._circuit_breaker.record_success()
            result.classification = classification
            result.is_task = classification.is_task

            if not classification.is_task:
                logger.info(
                    "Email %s classified as %s (%.2f confidence): %s",
                    message.entry_id,
                    classification.category,
                    classification.confidence,
                    classification.reason,
                )
                return result

            if classification.confidence < MIN_TASK_CONFIDENCE:
                logger.warning(
                    "Email %s classified as task but confidence too low "
                    "(%.2f < %.2f), skipping: %s",
                    message.entry_id,
                    classification.confidence,
                    MIN_TASK_CONFIDENCE,
                    classification.reason,
                )
                return result

            ticket_id = await self._create_ticket(message)
            result.ticket_id = str(ticket_id)

            await self._link_email_to_ticket(message.entry_id, ticket_id)

            final_state = await self._invoke_workflow(message, ticket_id)
            workflow_status = final_state.get("status", "UNKNOWN")
            result.workflow_status = workflow_status

            await self._persist_ticket_status(ticket_id, workflow_status)

            if workflow_status == "WAITING_FOR_INFORMATION":
                success = await self._create_missing_info_entry(
                    ticket_id, message, final_state
                )
                if not success:
                    logger.error(
                        "WAITING_FOR_INFORMATION but failed to create queue entry for %s",
                        ticket_id,
                    )
            elif workflow_status == "EXTRACTION_FAILED":
                logger.warning(
                    "Extraction failed for ticket %s, no follow-up email sent: %s",
                    ticket_id,
                    final_state.get("error", "Unknown error"),
                )

            logger.info(
                "Processed task email %s -> ticket %s (workflow: %s)",
                message.entry_id,
                ticket_id,
                workflow_status,
            )

        except Exception:
            self._circuit_breaker.record_failure()
            logger.exception("Failed to process email %s", message.entry_id)
            result.error = "Processing failed — see logs for details"

        return result

    async def _try_handle_reply(self, message: EmailMessage) -> "ReplyResult | None":
        """Check if this email is a reply to an existing ticket and route to ConversationHandler.

        Returns ReplyResult if the email was handled as a reply, None otherwise.
        """
        if not message.conversation_id:
            return None

        try:
            from backend.app.services.conversation_handler import (
                ConversationHandler,
                ReplyResult,
            )

            handler = self._conversation_handler or ConversationHandler()
            result = await handler.handle_reply(
                conversation_id=message.conversation_id,
                reply_email=message,
            )
            return result
        except Exception:
            logger.exception(
                "Error handling reply for conversation %s",
                message.conversation_id,
            )
            return None

    async def _create_ticket(self, message: EmailMessage) -> uuid.UUID:
        """Create a new ticket for a task email.

        Args:
            message: The incoming email message.

        Returns:
            The UUID of the newly created ticket.
        """
        async with async_session_factory() as session:
            ticket_repo = TicketRepository(session)
            ticket = await ticket_repo.create(
                client="Unknown",
                contact=message.sender,
                task_description=message.subject or "Untitled task",
                conversation_id=message.conversation_id,
            )
            await session.commit()
            return ticket.ticket_id

    async def _link_email_to_ticket(
        self, entry_id: str, ticket_id: uuid.UUID
    ) -> None:
        """Link an email record to its ticket.

        Args:
            entry_id: The Outlook entry ID of the email.
            ticket_id: The UUID of the ticket to link to.
        """
        async with async_session_factory() as session:
            email_repo = EmailRepository(session)
            email = await email_repo.get_by_entry_id(entry_id)
            if email is not None:
                email.ticket_id = ticket_id
                await session.commit()

    async def _invoke_workflow(
        self, message: EmailMessage, ticket_id: uuid.UUID
    ) -> dict[str, object]:
        """Invoke the LangGraph workflow for the new ticket.

        Args:
            message: The incoming email message.
            ticket_id: The UUID of the ticket to process.

        Returns:
            The final workflow state dictionary.
        """
        initial_state = {
            "ticket_id": str(ticket_id),
            "status": "",
            "parsed_data": None,
            "validation_result": None,
            "missing_fields": [],
            "error": None,
            "sender": message.sender,
            "subject": message.subject,
            "body": message.body,
        }

        wf = compile_workflow()
        return await asyncio.to_thread(wf.invoke, initial_state)

    async def _persist_ticket_status(
        self, ticket_id: uuid.UUID, status: str
    ) -> None:
        """Persist the workflow-computed status to the ticket in the database.

        Uses the state machine to validate the transition.  In non-strict
        mode (the default), invalid transitions are logged but still applied
        so that email processing is never blocked by state machine issues.

        Args:
            ticket_id: The UUID of the ticket to update.
            status: The new status string from the workflow.

        Raises:
            Exception: Re-raises any exception from transition_ticket after logging.
        """
        if status == "EXTRACTION_FAILED":
            logger.info(
                "Skipping status persistence for EXTRACTION_FAILED on ticket %s",
                ticket_id,
            )
            return
        try:
            target = TicketStatus(status)
            await transition_ticket(ticket_id, target, strict_mode=False)
        except Exception:
            logger.exception(
                "Failed to persist status %s for ticket %s", status, ticket_id
            )
            raise

    async def _create_missing_info_entry(
        self,
        ticket_id: uuid.UUID,
        message: EmailMessage,
        workflow_state: dict[str, object],
    ) -> bool:
        """Create a missing info queue entry when the workflow detects missing fields.

        Uses the EmailDraftAgent to generate an LLM-powered draft email.
        Falls back to a template-based draft if the LLM fails.

        Args:
            ticket_id: The UUID of the ticket.
            message: The original email message.
            workflow_state: The final workflow state dict.

        Returns:
            True if the queue entry was created successfully, False otherwise.
        """
        try:
            missing_fields = workflow_state.get("missing_fields", [])
            if not missing_fields:
                logger.warning(
                    "No missing fields in workflow state for ticket %s, "
                    "skipping queue entry",
                    ticket_id,
                )
                return False

            parsed_data = workflow_state.get("parsed_data") or {}
            client = parsed_data.get("client") if isinstance(parsed_data, dict) else None
            project_number = parsed_data.get("project_number") if isinstance(parsed_data, dict) else None
            task_description = parsed_data.get("task_description") if isinstance(parsed_data, dict) else None

            draft_agent = EmailDraftAgent()
            draft = await asyncio.to_thread(
                draft_agent.draft,
                ticket_id=str(ticket_id),
                sender=message.sender,
                subject=message.subject or "Your request",
                client=client,
                project_number=project_number,
                task_description=task_description,
                missing_fields=missing_fields,
                conversation_id=message.conversation_id,
            )

            queue = get_missing_info_queue()
            await queue.add_to_queue(
                ticket_id=str(ticket_id),
                draft=draft,
                missing_fields=missing_fields,
                confidence=0.0,
            )
            logger.info(
                "Added ticket %s to missing info queue (fields: %s)",
                ticket_id,
                missing_fields,
            )
            return True
        except Exception:
            logger.exception(
                "Failed to create missing info entry for ticket %s", ticket_id
            )
            return False
