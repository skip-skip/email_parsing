from __future__ import annotations

import logging
import uuid
from datetime import datetime

from backend.app.agents.email_draft_agent import DraftEmail
from backend.app.services.queues.queue_item import QueueItem

logger = logging.getLogger(__name__)


class MissingInfoQueue:
    def __init__(self) -> None:
        self._items: dict[uuid.UUID, QueueItem] = {}

    async def add_to_queue(
        self,
        ticket_id: str,
        draft: DraftEmail,
        missing_fields: list[str],
    ) -> QueueItem:
        ticket_uuid = uuid.UUID(ticket_id)
        item = QueueItem(
            ticket_id=ticket_uuid,
            draft_email=draft,
            missing_fields=missing_fields,
            created_at=datetime.now(),
            status="PENDING",
        )
        self._items[ticket_uuid] = item
        logger.info("Added ticket %s to missing info queue", ticket_id)
        return item

    async def get_queue(self) -> list[QueueItem]:
        return [item for item in self._items.values() if item.status == "PENDING"]

    async def get_item(self, ticket_id: str) -> QueueItem | None:
        ticket_uuid = uuid.UUID(ticket_id)
        return self._items.get(ticket_uuid)

    async def approve_item(
        self,
        ticket_id: str,
        edits: DraftEmail | None = None,
    ) -> QueueItem | None:
        ticket_uuid = uuid.UUID(ticket_id)
        item = self._items.get(ticket_uuid)
        if item is None:
            logger.warning("Queue item not found for ticket %s", ticket_id)
            return None

        if edits is not None:
            item.draft_email = edits

        item.status = "APPROVED"
        logger.info("Approved queue item for ticket %s", ticket_id)
        return item

    async def reject_item(
        self,
        ticket_id: str,
        reason: str | None = None,
    ) -> QueueItem | None:
        ticket_uuid = uuid.UUID(ticket_id)
        item = self._items.get(ticket_uuid)
        if item is None:
            logger.warning("Queue item not found for ticket %s", ticket_id)
            return None

        item.status = "REJECTED"
        logger.info(
            "Rejected queue item for ticket %s. Reason: %s",
            ticket_id,
            reason or "No reason provided",
        )
        return item

    async def update_draft(
        self,
        ticket_id: str,
        new_draft: DraftEmail,
    ) -> QueueItem | None:
        ticket_uuid = uuid.UUID(ticket_id)
        item = self._items.get(ticket_uuid)
        if item is None:
            logger.warning("Queue item not found for ticket %s", ticket_id)
            return None

        item.draft_email = new_draft
        logger.info("Updated draft for ticket %s", ticket_id)
        return item
