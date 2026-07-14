from __future__ import annotations

import logging
import uuid
from datetime import datetime

from sqlalchemy import select

from backend.app.agents.email_draft_agent import DraftEmail
from backend.app.models.missing_info_queue_record import MissingInfoQueueRecord
from backend.app.services.database import async_session_factory
from backend.app.services.database.repositories.ticket_repository import TicketRepository
from backend.app.services.queues.queue_item import QueueItem
from backend.app.services.outlook.base import EmailProvider

logger = logging.getLogger(__name__)

_missing_info_queue: MissingInfoQueue | None = None


def get_missing_info_queue() -> MissingInfoQueue:
    """Return the shared MissingInfoQueue singleton."""
    global _missing_info_queue
    if _missing_info_queue is None:
        _missing_info_queue = MissingInfoQueue()
    return _missing_info_queue


def _record_to_item(record: MissingInfoQueueRecord) -> QueueItem:
    draft_data = record.draft_json
    draft = DraftEmail(
        to=draft_data["to"],
        subject=draft_data["subject"],
        body=draft_data["body"],
        missing_fields=draft_data["missing_fields"],
        ticket_id=uuid.UUID(draft_data["ticket_id"]),
    )
    return QueueItem(
        ticket_id=record.ticket_id,
        draft_email=draft,
        missing_fields=record.missing_fields,
        confidence=record.confidence,
        created_at=record.created_at,
        status=record.status,
    )


class MissingInfoQueue:
    async def add_to_queue(
        self,
        ticket_id: str,
        draft: DraftEmail,
        missing_fields: list[str],
        confidence: float = 0.0,
    ) -> QueueItem:
        ticket_uuid = uuid.UUID(ticket_id)
        draft_json = {
            "to": draft.to,
            "subject": draft.subject,
            "body": draft.body,
            "missing_fields": draft.missing_fields,
            "ticket_id": str(draft.ticket_id),
        }
        async with async_session_factory() as session:
            record = MissingInfoQueueRecord(
                ticket_id=ticket_uuid,
                draft_json=draft_json,
                missing_fields=missing_fields,
                confidence=confidence,
                status="PENDING",
                created_at=datetime.now(),
            )
            session.add(record)
            await session.commit()
        logger.info("Added ticket %s to missing info queue", ticket_id)
        return QueueItem(
            ticket_id=ticket_uuid,
            draft_email=draft,
            missing_fields=missing_fields,
            confidence=confidence,
            created_at=record.created_at,
            status="PENDING",
        )

    async def get_queue(self) -> list[QueueItem]:
        async with async_session_factory() as session:
            result = await session.execute(
                select(MissingInfoQueueRecord).where(
                    MissingInfoQueueRecord.status.in_(["PENDING", "AWAITING_REPLY"])
                )
            )
            records = result.scalars().all()
            return [_record_to_item(r) for r in records]

    async def get_item(self, ticket_id: str) -> QueueItem | None:
        ticket_uuid = uuid.UUID(ticket_id)
        async with async_session_factory() as session:
            result = await session.execute(
                select(MissingInfoQueueRecord).where(
                    MissingInfoQueueRecord.ticket_id == ticket_uuid
                )
            )
            record = result.scalar_one_or_none()
            if record is None:
                return None
            return _record_to_item(record)

    async def approve_item(
        self,
        ticket_id: str,
        edits: DraftEmail | None = None,
        email_provider: EmailProvider | None = None,
    ) -> QueueItem | None:
        ticket_uuid = uuid.UUID(ticket_id)
        async with async_session_factory() as session:
            result = await session.execute(
                select(MissingInfoQueueRecord).where(
                    MissingInfoQueueRecord.ticket_id == ticket_uuid
                )
            )
            record = result.scalar_one_or_none()
            if record is None:
                logger.warning("Queue item not found for ticket %s", ticket_id)
                return None

            if edits is not None:
                record.draft_json = {
                    "to": edits.to,
                    "subject": edits.subject,
                    "body": edits.body,
                    "missing_fields": edits.missing_fields,
                    "ticket_id": str(edits.ticket_id),
                }

            record.status = "APPROVED"

            draft_data = record.draft_json
            conversation_id = draft_data.get("ticket_id", "")
            ticket_repo = TicketRepository(session)
            ticket = await ticket_repo.get_by_id(ticket_uuid)
            if ticket and ticket.conversation_id:
                conversation_id = ticket.conversation_id

            if email_provider is not None:
                try:
                    await email_provider.send_reply_all(
                        conversation_id, draft_data["body"]
                    )
                    record.status = "AWAITING_REPLY"
                    logger.info(
                        "Sent missing info email for ticket %s via reply-all",
                        ticket_id,
                    )
                except Exception:
                    record.status = "PENDING"
                    logger.exception(
                        "Failed to send missing info email for ticket %s, "
                        "item remains in PENDING for retry",
                        ticket_id,
                    )

            await session.commit()
            await session.refresh(record)
            logger.info("Approved queue item for ticket %s", ticket_id)
            return _record_to_item(record)

    async def reject_item(
        self,
        ticket_id: str,
        reason: str | None = None,
    ) -> QueueItem | None:
        ticket_uuid = uuid.UUID(ticket_id)
        async with async_session_factory() as session:
            result = await session.execute(
                select(MissingInfoQueueRecord).where(
                    MissingInfoQueueRecord.ticket_id == ticket_uuid
                )
            )
            record = result.scalar_one_or_none()
            if record is None:
                logger.warning("Queue item not found for ticket %s", ticket_id)
                return None

            record.status = "REJECTED"
            await session.commit()
            await session.refresh(record)
            logger.info(
                "Rejected queue item for ticket %s. Reason: %s",
                ticket_id,
                reason or "No reason provided",
            )
            return _record_to_item(record)

    async def update_draft(
        self,
        ticket_id: str,
        new_draft: DraftEmail,
    ) -> QueueItem | None:
        ticket_uuid = uuid.UUID(ticket_id)
        async with async_session_factory() as session:
            result = await session.execute(
                select(MissingInfoQueueRecord).where(
                    MissingInfoQueueRecord.ticket_id == ticket_uuid
                )
            )
            record = result.scalar_one_or_none()
            if record is None:
                logger.warning("Queue item not found for ticket %s", ticket_id)
                return None

            record.draft_json = {
                "to": new_draft.to,
                "subject": new_draft.subject,
                "body": new_draft.body,
                "missing_fields": new_draft.missing_fields,
                "ticket_id": str(new_draft.ticket_id),
            }
            await session.commit()
            await session.refresh(record)
            logger.info("Updated draft for ticket %s", ticket_id)
            return _record_to_item(record)
