from __future__ import annotations

import logging
import uuid
from datetime import datetime

from backend.app.agents.calendar_planning_agent import ScheduleBlock, ScheduleSuggestion
from backend.app.services.queues.scheduling_queue_item import SchedulingQueueItem

logger = logging.getLogger(__name__)


class SchedulingQueue:
    def __init__(self) -> None:
        self._items: dict[uuid.UUID, SchedulingQueueItem] = {}

    async def add_to_queue(
        self,
        ticket_id: str,
        suggestion: ScheduleSuggestion,
        confidence: float | None = None,
    ) -> SchedulingQueueItem:
        ticket_uuid = uuid.UUID(ticket_id)
        item = SchedulingQueueItem(
            ticket_id=ticket_uuid,
            suggestion=suggestion,
            confidence=confidence if confidence is not None else suggestion.confidence,
            status="PENDING",
            created_at=datetime.now(),
        )
        self._items[ticket_uuid] = item
        logger.info("Added ticket %s to scheduling queue", ticket_id)
        return item

    async def get_queue(self) -> list[SchedulingQueueItem]:
        return [
            item
            for item in self._items.values()
            if item.status == "PENDING"
        ]

    async def get_item(self, ticket_id: str) -> SchedulingQueueItem | None:
        ticket_uuid = uuid.UUID(ticket_id)
        return self._items.get(ticket_uuid)

    async def approve_schedule(
        self,
        ticket_id: str,
        selected_blocks: list[ScheduleBlock] | None = None,
    ) -> SchedulingQueueItem | None:
        ticket_uuid = uuid.UUID(ticket_id)
        item = self._items.get(ticket_uuid)
        if item is None:
            logger.warning("Scheduling queue item not found for ticket %s", ticket_id)
            return None

        if selected_blocks is not None:
            item.suggestion.blocks = selected_blocks
            item.suggestion.total_hours = sum(b.hours for b in selected_blocks)

        item.status = "APPROVED"
        logger.info("Approved schedule for ticket %s", ticket_id)
        return item

    async def decline_schedule(
        self,
        ticket_id: str,
        reason: str | None = None,
    ) -> SchedulingQueueItem | None:
        ticket_uuid = uuid.UUID(ticket_id)
        item = self._items.get(ticket_uuid)
        if item is None:
            logger.warning("Scheduling queue item not found for ticket %s", ticket_id)
            return None

        item.status = "DECLINED"
        logger.info(
            "Declined schedule for ticket %s. Reason: %s",
            ticket_id,
            reason or "No reason provided",
        )
        return item

    async def modify_schedule(
        self,
        ticket_id: str,
        modified_blocks: list[ScheduleBlock],
    ) -> SchedulingQueueItem | None:
        ticket_uuid = uuid.UUID(ticket_id)
        item = self._items.get(ticket_uuid)
        if item is None:
            logger.warning("Scheduling queue item not found for ticket %s", ticket_id)
            return None

        item.suggestion.blocks = modified_blocks
        item.suggestion.total_hours = sum(b.hours for b in modified_blocks)
        logger.info("Modified schedule for ticket %s", ticket_id)
        return item
