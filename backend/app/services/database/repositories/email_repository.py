from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.email import Email


class EmailRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_entry_id(self, entry_id: str) -> Email | None:
        result = await self._session.execute(
            select(Email).where(Email.entry_id == entry_id)
        )
        return result.scalar_one_or_none()

    async def get_by_conversation_id(self, conversation_id: str) -> list[Email]:
        result = await self._session.execute(
            select(Email).where(Email.conversation_id == conversation_id)
        )
        return list(result.scalars().all())

    async def create(
        self,
        conversation_id: str,
        entry_id: str,
        sender: str,
        subject: str,
        body: str,
        received_time: datetime,
        attachments: list[str] | None = None,
        ticket_id: uuid.UUID | None = None,
    ) -> Email:
        email = Email(
            conversation_id=conversation_id,
            entry_id=entry_id,
            sender=sender,
            subject=subject,
            body=body,
            received_time=received_time,
            attachments=attachments or [],
            ticket_id=ticket_id,
        )
        self._session.add(email)
        await self._session.flush()
        return email
