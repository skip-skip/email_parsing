from __future__ import annotations

import logging
import uuid
import uuid as uuid_mod
from dataclasses import dataclass
from datetime import datetime

from backend.app.agents.calendar_planning_agent import ScheduleBlock
from backend.app.services.database import async_session_factory
from backend.app.services.database.repositories.ticket_repository import (
    TicketRepository,
)

logger = logging.getLogger(__name__)


@dataclass
class CalendarEvent:
    event_id: str
    ticket_id: str
    subject: str
    start_time: datetime
    end_time: datetime
    body: str = ""


class CalendarManager:
    def __init__(self) -> None:
        self._events: dict[str, CalendarEvent] = {}

    async def create_events(
        self,
        ticket_id: str,
        blocks: list[ScheduleBlock],
        subject: str = "Work Block",
    ) -> list[CalendarEvent]:
        events: list[CalendarEvent] = []

        for block in blocks:
            event = CalendarEvent(
                event_id=f"evt-{uuid.uuid4().hex[:8]}",
                ticket_id=ticket_id,
                subject=subject,
                start_time=block.start_time,
                end_time=block.end_time,
                body=block.description,
            )
            self._events[event.event_id] = event
            events.append(event)
            logger.info(
                "Created calendar event %s for ticket %s",
                event.event_id,
                ticket_id,
            )

        async with async_session_factory() as session:
            ticket_repo = TicketRepository(session)
            ticket_uuid = uuid_mod.UUID(ticket_id)
            await ticket_repo.update(
                ticket_uuid,
                calendar_event_id=events[0].event_id if events else None,
                status="IN_PROGRESS",
            )
            await session.commit()

        return events

    async def update_events(
        self,
        ticket_id: str,
        new_blocks: list[ScheduleBlock],
        subject: str = "Work Block",
    ) -> list[CalendarEvent]:
        await self.cancel_events(ticket_id)
        return await self.create_events(ticket_id, new_blocks, subject)

    async def cancel_events(self, ticket_id: str) -> None:
        to_remove = [
            eid
            for eid, event in self._events.items()
            if event.ticket_id == ticket_id
        ]
        for eid in to_remove:
            del self._events[eid]
            logger.info("Cancelled calendar event %s", eid)

    async def get_events_for_ticket(
        self, ticket_id: str
    ) -> list[CalendarEvent]:
        return [
            event
            for event in self._events.values()
            if event.ticket_id == ticket_id
        ]
