from __future__ import annotations

import logging
from dataclasses import asdict

from backend.app.agents.merge_result import MergeResult
from backend.app.agents.email_parsing_agent import EmailParsingAgent
from backend.app.services.database import async_session_factory
from backend.app.services.database.repositories.ticket_repository import TicketRepository
from backend.app.services.database.repositories.email_repository import EmailRepository
from shared.schemas.email import ParsedEmail, EmailMessage

logger = logging.getLogger(__name__)

MERGEABLE_FIELDS = [
    "client",
    "project_number",
    "task_description",
    "deadline",
    "budget_hours",
]


class ConversationTracker:
    """Tracks email conversation threads and merges new information into tickets.

    When a reply arrives for an existing ticket, this agent parses the new
    email and merges any updated fields (client, project_number, deadline, etc.)
    into the ticket record.
    """

    def __init__(self, parsing_agent: EmailParsingAgent | None = None) -> None:
        """Initialize the tracker.

        Args:
            parsing_agent: Agent for parsing email content. Creates a default if None.
        """
        self._parsing_agent = parsing_agent or EmailParsingAgent()

    async def merge(
        self,
        ticket_id: str,
        new_email: EmailMessage,
        previous_emails: list[EmailMessage],
    ) -> MergeResult:
        """Parse a new reply email and merge updated fields into the ticket.

        Args:
            ticket_id: The ticket to update.
            new_email: The incoming reply email.
            previous_emails: Earlier emails in the same conversation.

        Returns:
            MergeResult describing which fields were updated and their old/new values.
        """
        parsed = await self._parsing_agent.parse(
            sender=new_email.sender,
            subject=new_email.subject,
            body=new_email.body,
            received_time=new_email.received_time,
            ticket_id=ticket_id,
        )

        import uuid
        ticket_uuid = uuid.UUID(ticket_id)

        async with async_session_factory() as session:
            ticket_repo = TicketRepository(session)
            ticket = await ticket_repo.get_by_id(ticket_uuid)

            if ticket is None:
                logger.warning("Ticket %s not found", ticket_id)
                return MergeResult(ticket_id=ticket_uuid)

            merge_result = MergeResult(ticket_id=ticket_uuid)

            for field_name in MERGEABLE_FIELDS:
                new_value = getattr(parsed, field_name, None)
                old_value = getattr(ticket, field_name, None)

                if new_value is not None:
                    if old_value is None:
                        merge_result.updated_fields.append(field_name)
                        merge_result.previous_values[field_name] = old_value
                        merge_result.new_values[field_name] = new_value
                        setattr(ticket, field_name, new_value)
                    elif new_value != old_value:
                        merge_result.updated_fields.append(field_name)
                        merge_result.previous_values[field_name] = old_value
                        merge_result.new_values[field_name] = new_value
                        setattr(ticket, field_name, new_value)

            if merge_result.updated_fields:
                from sqlalchemy import func
                ticket.updated_at = func.now()

            await session.commit()

        return merge_result
