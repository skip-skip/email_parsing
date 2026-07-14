from __future__ import annotations

import logging
import uuid
from datetime import datetime

from sqlalchemy import select

from backend.app.agents.calendar_planning_agent import ScheduleBlock, ScheduleSuggestion
from backend.app.models.scheduling_queue_record import SchedulingQueueRecord
from backend.app.services.database import async_session_factory
from backend.app.services.database.repositories.ticket_repository import TicketRepository
from backend.app.services.outlook.base import EmailProvider
from backend.app.services.queues.scheduling_queue_item import SchedulingQueueItem
from backend.app.workflows.state_manager import transition_ticket
from backend.app.workflows.states import TicketStatus

logger = logging.getLogger(__name__)

_scheduling_queue: SchedulingQueue | None = None


def get_scheduling_queue() -> SchedulingQueue:
    """Return the shared SchedulingQueue singleton."""
    global _scheduling_queue
    if _scheduling_queue is None:
        _scheduling_queue = SchedulingQueue()
    return _scheduling_queue


def _blocks_to_json(blocks: list[ScheduleBlock]) -> list[dict[str, object]]:
    return [
        {
            "start_time": b.start_time.isoformat(),
            "end_time": b.end_time.isoformat(),
            "hours": b.hours,
            "description": b.description,
        }
        for b in blocks
    ]


def _json_to_blocks(data: list[dict[str, object]]) -> list[ScheduleBlock]:
    return [
        ScheduleBlock(
            start_time=datetime.fromisoformat(str(b["start_time"])),
            end_time=datetime.fromisoformat(str(b["end_time"])),
            hours=float(b["hours"]),
            description=str(b.get("description", "")),
        )
        for b in data
    ]


def _suggestion_to_json(suggestion: ScheduleSuggestion) -> dict[str, object]:
    return {
        "blocks": _blocks_to_json(suggestion.blocks),
        "total_hours": suggestion.total_hours,
        "fits_deadline": suggestion.fits_deadline,
        "confidence": suggestion.confidence,
    }


def _json_to_suggestion(data: dict[str, object]) -> ScheduleSuggestion:
    return ScheduleSuggestion(
        blocks=_json_to_blocks(data["blocks"]),
        total_hours=float(data["total_hours"]),
        fits_deadline=bool(data["fits_deadline"]),
        confidence=float(data["confidence"]),
    )


def _record_to_item(record: SchedulingQueueRecord) -> SchedulingQueueItem:
    suggestion = _json_to_suggestion(record.suggestion_json)
    return SchedulingQueueItem(
        ticket_id=record.ticket_id,
        suggestion=suggestion,
        confidence=record.confidence,
        status=record.status,
        created_at=record.created_at,
    )


class SchedulingQueue:
    async def add_to_queue(
        self,
        ticket_id: str,
        suggestion: ScheduleSuggestion,
        confidence: float | None = None,
    ) -> SchedulingQueueItem:
        ticket_uuid = uuid.UUID(ticket_id)
        suggestion_json = _suggestion_to_json(suggestion)
        async with async_session_factory() as session:
            record = SchedulingQueueRecord(
                ticket_id=ticket_uuid,
                suggestion_json=suggestion_json,
                confidence=confidence if confidence is not None else suggestion.confidence,
                status="PENDING",
                created_at=datetime.now(),
            )
            session.add(record)
            await session.commit()
        logger.info("Added ticket %s to scheduling queue", ticket_id)
        return _record_to_item(record)

    async def get_queue(self) -> list[SchedulingQueueItem]:
        async with async_session_factory() as session:
            result = await session.execute(
                select(SchedulingQueueRecord).where(
                    SchedulingQueueRecord.status == "PENDING"
                )
            )
            records = result.scalars().all()
            return [_record_to_item(r) for r in records]

    async def get_item(self, ticket_id: str) -> SchedulingQueueItem | None:
        ticket_uuid = uuid.UUID(ticket_id)
        async with async_session_factory() as session:
            result = await session.execute(
                select(SchedulingQueueRecord).where(
                    SchedulingQueueRecord.ticket_id == ticket_uuid
                )
            )
            record = result.scalar_one_or_none()
            if record is None:
                return None
            return _record_to_item(record)

    async def approve_schedule(
        self,
        ticket_id: str,
        selected_blocks: list[ScheduleBlock] | None = None,
        email_provider: EmailProvider | None = None,
    ) -> SchedulingQueueItem | None:
        ticket_uuid = uuid.UUID(ticket_id)
        async with async_session_factory() as session:
            result = await session.execute(
                select(SchedulingQueueRecord).where(
                    SchedulingQueueRecord.ticket_id == ticket_uuid
                )
            )
            record = result.scalar_one_or_none()
            if record is None:
                logger.warning("Scheduling queue item not found for ticket %s", ticket_id)
                return None

            if selected_blocks is not None:
                suggestion = _json_to_suggestion(record.suggestion_json)
                suggestion.blocks = selected_blocks
                suggestion.total_hours = sum(b.hours for b in selected_blocks)
                record.suggestion_json = _suggestion_to_json(suggestion)

            record.status = "APPROVED"
            await session.commit()
            await session.refresh(record)

            try:
                await transition_ticket(ticket_uuid, TicketStatus.IN_PROGRESS, strict_mode=False)
            except ValueError:
                logger.warning("Ticket %s not found for status transition", ticket_id)

            if email_provider is not None:
                ticket_repo = TicketRepository(session)
                ticket = await ticket_repo.get_by_id(ticket_uuid)
                if ticket is not None and ticket.conversation_id:
                    try:
                        suggestion = _json_to_suggestion(record.suggestion_json)
                        blocks_text = "\n".join(
                            f"  - {b.start_time.strftime('%Y-%m-%d %H:%M')} to {b.end_time.strftime('%Y-%m-%d %H:%M')} ({b.hours}h): {b.description}"
                            for b in suggestion.blocks
                        )
                        body = (
                            f"Hello,\n\n"
                            f"Your task has been scheduled:\n\n"
                            f"{blocks_text}\n\n"
                            f"Total hours: {suggestion.total_hours}\n\n"
                            f"Thank you."
                        )
                        await email_provider.send_reply_all(
                            conversation_id=ticket.conversation_id,
                            body=body,
                        )
                        logger.info("Sent schedule acceptance email for ticket %s", ticket_id)
                    except Exception:
                        logger.exception("Failed to send schedule email for ticket %s", ticket_id)

            logger.info("Approved schedule for ticket %s", ticket_id)
            return _record_to_item(record)

    async def decline_schedule(
        self,
        ticket_id: str,
        reason: str | None = None,
        email_provider: EmailProvider | None = None,
    ) -> SchedulingQueueItem | None:
        ticket_uuid = uuid.UUID(ticket_id)
        async with async_session_factory() as session:
            result = await session.execute(
                select(SchedulingQueueRecord).where(
                    SchedulingQueueRecord.ticket_id == ticket_uuid
                )
            )
            record = result.scalar_one_or_none()
            if record is None:
                logger.warning("Scheduling queue item not found for ticket %s", ticket_id)
                return None

            record.status = "DECLINED"
            await session.commit()
            await session.refresh(record)

            try:
                await transition_ticket(ticket_uuid, TicketStatus.WAITING_FOR_INFORMATION, strict_mode=False)
            except ValueError:
                logger.warning("Ticket %s not found for status transition", ticket_id)

            if email_provider is not None:
                ticket_repo = TicketRepository(session)
                ticket = await ticket_repo.get_by_id(ticket_uuid)
                if ticket is not None and ticket.conversation_id:
                    try:
                        reason_text = f"\nReason: {reason}" if reason else ""
                        body = (
                            f"Hello,\n\n"
                            f"Unfortunately, we were unable to schedule your task at this time.{reason_text}\n\n"
                            f"Please let us know if you have any questions."
                        )
                        await email_provider.send_reply_all(
                            conversation_id=ticket.conversation_id,
                            body=body,
                        )
                        logger.info("Sent schedule decline email for ticket %s", ticket_id)
                    except Exception:
                        logger.exception("Failed to send decline email for ticket %s", ticket_id)

            logger.info(
                "Declined schedule for ticket %s. Reason: %s",
                ticket_id,
                reason or "No reason provided",
            )
            return _record_to_item(record)

    async def modify_schedule(
        self,
        ticket_id: str,
        modified_blocks: list[ScheduleBlock],
    ) -> SchedulingQueueItem | None:
        ticket_uuid = uuid.UUID(ticket_id)
        async with async_session_factory() as session:
            result = await session.execute(
                select(SchedulingQueueRecord).where(
                    SchedulingQueueRecord.ticket_id == ticket_uuid
                )
            )
            record = result.scalar_one_or_none()
            if record is None:
                logger.warning("Scheduling queue item not found for ticket %s", ticket_id)
                return None

            suggestion = _json_to_suggestion(record.suggestion_json)
            suggestion.blocks = modified_blocks
            suggestion.total_hours = sum(b.hours for b in modified_blocks)
            record.suggestion_json = _suggestion_to_json(suggestion)

            await session.commit()
            await session.refresh(record)
            logger.info("Modified schedule for ticket %s", ticket_id)
            return _record_to_item(record)
