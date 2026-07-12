from __future__ import annotations

import logging
from dataclasses import dataclass

from backend.app.agents.conversation_tracker import ConversationTracker
from backend.app.services.database import async_session_factory
from backend.app.services.database.repositories.email_repository import EmailRepository
from backend.app.services.database.repositories.ticket_repository import (
    TicketRepository,
)
from backend.app.services.queues.missing_info_queue import MissingInfoQueue
from backend.app.services.validation.validator import TicketValidator
from backend.app.workflows.state_manager import transition_ticket
from backend.app.workflows.states import TicketStatus
from shared.schemas.email import EmailMessage

logger = logging.getLogger(__name__)


@dataclass
class ReplyResult:
    ticket_id: str
    status: str
    updated_fields: list[str]
    missing_fields: list[str]
    is_complete: bool


class ConversationHandler:
    def __init__(
        self,
        tracker: ConversationTracker | None = None,
        validator: TicketValidator | None = None,
        queue: MissingInfoQueue | None = None,
    ) -> None:
        self._tracker = tracker or ConversationTracker()
        self._validator = validator or TicketValidator()
        self._queue = queue or MissingInfoQueue()

    async def handle_reply(
        self,
        conversation_id: str,
        reply_email: EmailMessage,
    ) -> ReplyResult | None:
        async with async_session_factory() as session:
            ticket_repo = TicketRepository(session)
            email_repo = EmailRepository(session)

            ticket = await ticket_repo.get_by_conversation_id(conversation_id)
            if ticket is None:
                logger.warning(
                    "No ticket found for conversation %s", conversation_id
                )
                return None

            if ticket.status != TicketStatus.WAITING_FOR_INFORMATION.value:
                logger.info(
                    "Ticket %s is not in WAITING_FOR_INFORMATION (current: %s)",
                    ticket.ticket_id,
                    ticket.status,
                )
                return None

            previous_emails = await email_repo.get_by_conversation_id(
                conversation_id
            )

            merge_result = await self._tracker.merge(
                ticket_id=str(ticket.ticket_id),
                new_email=reply_email,
                previous_emails=previous_emails,
            )

            ticket_data = {
                "task_description": ticket.task_description,
                "project_number": ticket.project_number,
                "budget_hours": ticket.budget_hours,
                "deadline": (
                    ticket.deadline.isoformat() if ticket.deadline else None
                ),
            }

            for field in merge_result.updated_fields:
                if field in ticket_data:
                    new_val = merge_result.new_values.get(field)
                    if field == "deadline" and new_val is not None:
                        if hasattr(new_val, "isoformat"):
                            ticket_data[field] = new_val.isoformat()
                        else:
                            ticket_data[field] = str(new_val)
                    else:
                        ticket_data[field] = new_val

            validation = self._validator.validate(ticket_data)

            if validation.is_complete:
                await transition_ticket(
                    ticket.ticket_id,
                    TicketStatus.READY_FOR_SCHEDULING,
                )
                logger.info(
                    "Ticket %s now complete, moved to READY_FOR_SCHEDULING",
                    ticket.ticket_id,
                )
            else:
                logger.info(
                    "Ticket %s still incomplete, missing: %s",
                    ticket.ticket_id,
                    validation.missing_fields,
                )

            return ReplyResult(
                ticket_id=str(ticket.ticket_id),
                status=(
                    TicketStatus.READY_FOR_SCHEDULING.value
                    if validation.is_complete
                    else TicketStatus.WAITING_FOR_INFORMATION.value
                ),
                updated_fields=merge_result.updated_fields,
                missing_fields=validation.missing_fields,
                is_complete=validation.is_complete,
            )
