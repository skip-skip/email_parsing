from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.ticket import Ticket


class TicketRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, ticket_id: uuid.UUID) -> Ticket | None:
        result = await self._session.execute(
            select(Ticket).where(Ticket.ticket_id == ticket_id)
        )
        return result.scalar_one_or_none()

    async def get_by_conversation_id(self, conversation_id: str) -> Ticket | None:
        result = await self._session.execute(
            select(Ticket).where(Ticket.conversation_id == conversation_id)
        )
        return result.scalar_one_or_none()

    async def get_by_status(self, status: str) -> list[Ticket]:
        result = await self._session.execute(
            select(Ticket).where(Ticket.status == status)
        )
        return list(result.scalars().all())

    async def create(
        self,
        client: str,
        contact: str,
        task_description: str,
        project_number: str | None = None,
        deadline: object | None = None,
        budget_hours: float | None = None,
        estimated_hours: float | None = None,
        priority: int = 0,
        conversation_id: str | None = None,
    ) -> Ticket:
        ticket = Ticket(
            client=client,
            contact=contact,
            task_description=task_description,
            project_number=project_number,
            deadline=deadline,
            budget_hours=budget_hours,
            estimated_hours=estimated_hours,
            priority=priority,
            conversation_id=conversation_id,
        )
        self._session.add(ticket)
        await self._session.flush()
        return ticket

    async def update(self, ticket_id: uuid.UUID, **fields: object) -> Ticket | None:
        ticket = await self.get_by_id(ticket_id)
        if ticket is None:
            return None
        for key, value in fields.items():
            if hasattr(ticket, key):
                setattr(ticket, key, value)
        await self._session.flush()
        return ticket

    async def delete(self, ticket_id: uuid.UUID) -> None:
        ticket = await self.get_by_id(ticket_id)
        if ticket is not None:
            await self._session.delete(ticket)
            await self._session.flush()
