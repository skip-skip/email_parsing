from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.calendar_event import CalendarEvent


class CalendarRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_ticket_id(self, ticket_id: uuid.UUID) -> list[CalendarEvent]:
        result = await self._session.execute(
            select(CalendarEvent).where(CalendarEvent.ticket_id == ticket_id)
        )
        return list(result.scalars().all())

    async def create(
        self,
        ticket_id: uuid.UUID,
        start_time: datetime,
        end_time: datetime,
        duration: float,
        status: str = "PROPOSED",
        outlook_event_id: str | None = None,
    ) -> CalendarEvent:
        event = CalendarEvent(
            ticket_id=ticket_id,
            start_time=start_time,
            end_time=end_time,
            duration=duration,
            status=status,
            outlook_event_id=outlook_event_id,
        )
        self._session.add(event)
        await self._session.flush()
        return event

    async def update(
        self, calendar_event_id: uuid.UUID, **fields: object
    ) -> CalendarEvent | None:
        result = await self._session.execute(
            select(CalendarEvent).where(
                CalendarEvent.calendar_event_id == calendar_event_id
            )
        )
        event = result.scalar_one_or_none()
        if event is None:
            return None
        for key, value in fields.items():
            if hasattr(event, key):
                setattr(event, key, value)
        await self._session.flush()
        return event
