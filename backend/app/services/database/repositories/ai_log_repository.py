from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.ai_log import AILog


class AILogRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(
        self,
        model: str,
        prompt_version: str,
        prompt: str,
        response: str,
        ticket_id: uuid.UUID | None = None,
        parsed_json: dict | None = None,
        confidence: float | None = None,
        execution_time_ms: int | None = None,
    ) -> AILog:
        log = AILog(
            model=model,
            prompt_version=prompt_version,
            prompt=prompt,
            response=response,
            ticket_id=ticket_id,
            parsed_json=parsed_json,
            confidence=confidence,
            execution_time_ms=execution_time_ms,
        )
        self._session.add(log)
        await self._session.flush()
        return log

    async def get_by_ticket_id(self, ticket_id: uuid.UUID) -> list[AILog]:
        result = await self._session.execute(
            select(AILog).where(AILog.ticket_id == ticket_id)
        )
        return list(result.scalars().all())
