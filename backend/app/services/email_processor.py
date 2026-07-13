"""Email processor service — bridges Outlook monitor to LangGraph workflow.

Classifies incoming emails, creates tickets for task requests, and
invokes the workflow for automatic processing.
"""
from __future__ import annotations

import asyncio
import logging
import uuid
from dataclasses import dataclass, field

from backend.app.agents.email_classification_agent import (
    ClassificationResult,
    EmailClassificationAgent,
)
from backend.app.services.database import async_session_factory
from backend.app.services.database.repositories.email_repository import (
    EmailRepository,
)
from backend.app.services.database.repositories.ticket_repository import (
    TicketRepository,
)
from backend.app.services.outlook.models import EmailMessage
from backend.app.workflows.graph import compile_workflow

logger = logging.getLogger(__name__)


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
    ) -> None:
        self._classifier = classification_agent or EmailClassificationAgent()

    async def process_new_email(self, message: EmailMessage) -> ProcessingResult:
        """Process a new email through the classification and workflow pipeline.

        Args:
            message: The incoming email message from Outlook.

        Returns:
            ProcessingResult with classification, ticket, and workflow status.
        """
        result = ProcessingResult(entry_id=message.entry_id)

        try:
            classification = await self._classifier.classify(
                sender=message.sender,
                subject=message.subject,
                body=message.body,
            )
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

            ticket_id = await self._create_ticket(message)
            result.ticket_id = str(ticket_id)

            await self._link_email_to_ticket(message.entry_id, ticket_id)

            workflow_status = await self._invoke_workflow(message, ticket_id)
            result.workflow_status = workflow_status

            logger.info(
                "Processed task email %s -> ticket %s (workflow: %s)",
                message.entry_id,
                ticket_id,
                workflow_status,
            )

        except Exception:
            logger.exception("Failed to process email %s", message.entry_id)
            result.error = "Processing failed — see logs for details"

        return result

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
    ) -> str:
        """Invoke the LangGraph workflow for the new ticket.

        Args:
            message: The incoming email message.
            ticket_id: The UUID of the ticket to process.

        Returns:
            The final workflow status string.
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
        final_state = await asyncio.to_thread(wf.invoke, initial_state)
        return final_state.get("status", "UNKNOWN")
