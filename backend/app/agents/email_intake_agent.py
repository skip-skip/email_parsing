from __future__ import annotations

import uuid
from dataclasses import dataclass

from backend.app.services.database import async_session_factory
from backend.app.services.database.repositories.email_repository import EmailRepository
from backend.app.services.database.repositories.ticket_repository import (
    TicketRepository,
)
from backend.app.services.outlook.models import EmailMessage


@dataclass
class IntakeResponse:
    email_id: uuid.UUID
    is_new_thread: bool
    existing_ticket_id: uuid.UUID | None
    ready_for_parsing: bool


class EmailIntakeAgent:
    """Processes incoming emails and creates initial database records.

    Checks for duplicate emails (by EntryID) and determines whether
    the email starts a new conversation thread or continues an existing
    ticket's conversation.
    """

    async def process(self, message: EmailMessage) -> IntakeResponse:
        """Process a new email message.

        Creates the email record in the database and determines whether
        this is a new conversation thread or a reply to an existing ticket.

        Args:
            message: The incoming email message from Outlook.

        Returns:
            IntakeResponse with email ID, thread status, and parsing readiness.
        """
        async with async_session_factory() as session:
            email_repo = EmailRepository(session)
            ticket_repo = TicketRepository(session)

            existing = await email_repo.get_by_entry_id(message.entry_id)
            if existing is not None:
                return IntakeResponse(
                    email_id=existing.email_id,
                    is_new_thread=False,
                    existing_ticket_id=existing.ticket_id,
                    ready_for_parsing=False,
                )

            existing_ticket = await ticket_repo.get_by_conversation_id(
                message.conversation_id
            )

            is_new_thread = existing_ticket is None
            ticket_id = None

            email = await email_repo.create(
                conversation_id=message.conversation_id,
                entry_id=message.entry_id,
                sender=message.sender,
                subject=message.subject,
                body=message.body,
                received_time=message.received_time,
                attachments=message.attachments,
                ticket_id=ticket_id,
            )
            await session.commit()

            return IntakeResponse(
                email_id=email.email_id,
                is_new_thread=is_new_thread,
                existing_ticket_id=ticket_id,
                ready_for_parsing=True,
            )
