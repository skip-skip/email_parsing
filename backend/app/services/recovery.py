"""Recovery mechanism for ticket/queue status drift.

Detects orphaned tickets (tickets in WAITING_FOR_INFORMATION or AWAITING_REPLY
with no queue entry) and mismatched queue entries (queue entries where ticket
status doesn't match).
"""

from __future__ import annotations

import logging
import uuid
from dataclasses import dataclass

from sqlalchemy import select

from backend.app.models.missing_info_queue_record import MissingInfoQueueRecord
from backend.app.models.scheduling_queue_record import SchedulingQueueRecord
from backend.app.models.ticket import Ticket
from backend.app.services.database import async_session_factory

logger = logging.getLogger(__name__)


@dataclass
class RecoveryIssue:
    """Represents a detected recovery issue."""

    ticket_id: uuid.UUID
    issue_type: str
    description: str
    ticket_status: str
    queue_entry_exists: bool


async def find_orphaned_tickets() -> list[RecoveryIssue]:
    """Find tickets in WAITING_FOR_INFORMATION or AWAITING_REPLY with no queue entry.

    Returns:
        List of RecoveryIssue objects for orphaned tickets.
    """
    issues: list[RecoveryIssue] = []

    async with async_session_factory() as session:
        # Find tickets in WAITING_FOR_INFORMATION
        result = await session.execute(
            select(Ticket).where(
                Ticket.status.in_(["WAITING_FOR_INFORMATION", "AWAITING_REPLY"])
            )
        )
        tickets = result.scalars().all()

        for ticket in tickets:
            # Check if ticket has a queue entry
            queue_result = await session.execute(
                select(MissingInfoQueueRecord).where(
                    MissingInfoQueueRecord.ticket_id == ticket.ticket_id
                )
            )
            queue_entry = queue_result.scalar_one_or_none()

            if queue_entry is None:
                issues.append(
                    RecoveryIssue(
                        ticket_id=ticket.ticket_id,
                        issue_type="ORPHANED_TICKET",
                        description=f"Ticket in {ticket.status} has no missing info queue entry",
                        ticket_status=ticket.status,
                        queue_entry_exists=False,
                    )
                )

    return issues


async def find_mismatched_queue_entries() -> list[RecoveryIssue]:
    """Find queue entries where ticket status doesn't match queue entry status.

    Returns:
        List of RecoveryIssue objects for mismatched queue entries.
    """
    issues: list[RecoveryIssue] = []

    async with async_session_factory() as session:
        # Check missing info queue entries
        result = await session.execute(select(MissingInfoQueueRecord))
        queue_records = result.scalars().all()

        for record in queue_records:
            # Get the ticket
            ticket_result = await session.execute(
                select(Ticket).where(Ticket.ticket_id == record.ticket_id)
            )
            ticket = ticket_result.scalar_one_or_none()

            if ticket is None:
                issues.append(
                    RecoveryIssue(
                        ticket_id=record.ticket_id,
                        issue_type="MISSING_TICKET",
                        description=f"Queue entry exists but ticket not found",
                        ticket_status="MISSING",
                        queue_entry_exists=True,
                    )
                )
            elif record.status == "PENDING" and ticket.status not in [
                "WAITING_FOR_INFORMATION",
                "AWAITING_REPLY",
            ]:
                issues.append(
                    RecoveryIssue(
                        ticket_id=record.ticket_id,
                        issue_type="STATUS_MISMATCH",
                        description=f"Queue entry is PENDING but ticket status is {ticket.status}",
                        ticket_status=ticket.status,
                        queue_entry_exists=True,
                    )
                )

    return issues


async def get_recovery_report() -> dict[str, list[RecoveryIssue]]:
    """Get a full recovery report.

    Returns:
        Dictionary with 'orphaned_tickets' and 'mismatched_queue_entries' keys.
    """
    orphaned = await find_orphaned_tickets()
    mismatched = await find_mismatched_queue_entries()

    if orphaned:
        logger.warning("Found %d orphaned tickets", len(orphaned))
    if mismatched:
        logger.warning("Found %d mismatched queue entries", len(mismatched))

    return {
        "orphaned_tickets": orphaned,
        "mismatched_queue_entries": mismatched,
    }
