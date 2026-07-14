from __future__ import annotations

import logging
import uuid

from backend.app.services.database import async_session_factory
from backend.app.services.database.repositories.ai_log_repository import AILogRepository
from backend.app.services.database.repositories.ticket_repository import (
    TicketRepository,
)
from backend.app.workflows.states import TicketStatus
from backend.app.workflows.transitions import InvalidTransitionError, can_transition

logger = logging.getLogger(__name__)


async def transition_ticket(
    ticket_id: uuid.UUID,
    target_status: TicketStatus,
    *,
    strict_mode: bool = False,
) -> object:
    async with async_session_factory() as session:
        ticket_repo = TicketRepository(session)
        log_repo = AILogRepository(session)

        ticket = await ticket_repo.get_by_id(ticket_id)
        if ticket is None:
            raise ValueError(f"Ticket {ticket_id} not found")

        current_status = TicketStatus(ticket.status)

        if not can_transition(current_status, target_status):
            if strict_mode:
                raise InvalidTransitionError(current_status, target_status)
            logger.warning(
                "Invalid transition %s -> %s for ticket %s (non-strict, allowing)",
                current_status.value,
                target_status.value,
                ticket_id,
            )

        previous_status = current_status.value
        ticket = await ticket_repo.update(
            ticket_id, status=target_status.value
        )

        await log_repo.create(
            model="state_machine",
            prompt_version="v1.0.0",
            prompt=f"transition:{previous_status}->{target_status.value}",
            response=f"ticket_id={ticket_id}",
            ticket_id=ticket_id,
            parsed_json={
                "previous_status": previous_status,
                "new_status": target_status.value,
            },
        )

        await session.commit()

        logger.info(
            "Ticket %s transitioned from %s to %s",
            ticket_id,
            previous_status,
            target_status.value,
        )

        return ticket
