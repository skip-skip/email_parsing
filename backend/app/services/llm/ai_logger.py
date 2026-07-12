from __future__ import annotations

import time
import uuid
from collections.abc import Generator
from contextlib import contextmanager
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.ai_log import AILog
from backend.app.services.database.repositories.ai_log_repository import AILogRepository


@contextmanager
def measure_time() -> Generator[dict[str, float | None], None, None]:
    result: dict[str, float | None] = {"elapsed_ms": None}
    start = time.perf_counter()
    try:
        yield result
    finally:
        elapsed = (time.perf_counter() - start) * 1000
        result["elapsed_ms"] = elapsed


async def log_interaction(
    session: AsyncSession,
    *,
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
    repo = AILogRepository(session)
    log = await repo.create(
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
    await session.commit()
    return log


class AILogger:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._repo = AILogRepository(session)

    async def log(
        self,
        *,
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
        log_entry = await self._repo.create(
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
        await self._session.commit()
        return log_entry
