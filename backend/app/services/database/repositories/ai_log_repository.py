from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import func, select
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
        parsed_json: dict[str, Any] | None = None,
        confidence: float | None = None,
        execution_time_ms: int | None = None,
        input_tokens: int | None = None,
        output_tokens: int | None = None,
        success: bool = True,
        error_message: str | None = None,
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
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            success=success,
            error_message=error_message,
        )
        self._session.add(log)
        await self._session.flush()
        return log

    async def get_by_ticket_id(self, ticket_id: uuid.UUID) -> list[AILog]:
        result = await self._session.execute(
            select(AILog).where(AILog.ticket_id == ticket_id)
        )
        return list(result.scalars().all())

    async def list_logs(
        self,
        *,
        offset: int = 0,
        limit: int = 50,
        model: str | None = None,
        prompt_version: str | None = None,
        success: bool | None = None,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
    ) -> list[AILog]:
        stmt = select(AILog)
        if model is not None:
            stmt = stmt.where(AILog.model == model)
        if prompt_version is not None:
            stmt = stmt.where(AILog.prompt_version == prompt_version)
        if success is not None:
            stmt = stmt.where(AILog.success == success)
        if date_from is not None:
            stmt = stmt.where(AILog.created_at >= date_from)
        if date_to is not None:
            stmt = stmt.where(AILog.created_at <= date_to)
        stmt = stmt.order_by(AILog.created_at.desc()).offset(offset).limit(limit)
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def count_logs(
        self,
        *,
        model: str | None = None,
        prompt_version: str | None = None,
        success: bool | None = None,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
    ) -> int:
        stmt = select(func.count()).select_from(AILog)
        if model is not None:
            stmt = stmt.where(AILog.model == model)
        if prompt_version is not None:
            stmt = stmt.where(AILog.prompt_version == prompt_version)
        if success is not None:
            stmt = stmt.where(AILog.success == success)
        if date_from is not None:
            stmt = stmt.where(AILog.created_at >= date_from)
        if date_to is not None:
            stmt = stmt.where(AILog.created_at <= date_to)
        result = await self._session.execute(stmt)
        return result.scalar_one()

    async def get_stats(self) -> dict[str, Any]:
        total = await self.count_logs()
        success_count_result = await self._session.execute(
            select(func.count()).select_from(AILog).where(AILog.success.is_(True))
        )
        success_count = success_count_result.scalar_one()

        avg_time_result = await self._session.execute(
            select(func.avg(AILog.execution_time_ms))
        )
        avg_time = avg_time_result.scalar_one() or 0.0

        avg_confidence_result = await self._session.execute(
            select(func.avg(AILog.confidence))
        )
        avg_confidence = avg_confidence_result.scalar_one() or 0.0

        total_input_tokens_result = await self._session.execute(
            select(func.sum(AILog.input_tokens))
        )
        total_input_tokens = total_input_tokens_result.scalar_one() or 0

        total_output_tokens_result = await self._session.execute(
            select(func.sum(AILog.output_tokens))
        )
        total_output_tokens = total_output_tokens_result.scalar_one() or 0

        model_counts_result = await self._session.execute(
            select(AILog.model, func.count()).group_by(AILog.model)
        )
        model_counts = {row[0]: row[1] for row in model_counts_result.all()}

        return {
            "total_interactions": total,
            "successful_interactions": success_count,
            "failed_interactions": total - success_count,
            "success_rate": (success_count / total * 100) if total > 0 else 0.0,
            "avg_execution_time_ms": round(float(avg_time), 2),
            "avg_confidence": round(float(avg_confidence), 4),
            "total_input_tokens": total_input_tokens,
            "total_output_tokens": total_output_tokens,
            "model_counts": model_counts,
        }
