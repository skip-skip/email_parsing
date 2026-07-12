from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.services.database import get_db
from backend.app.services.database.repositories.ai_log_repository import AILogRepository

router = APIRouter(prefix="/api/ai-logs", tags=["ai-logs"])


class AILogResponse(BaseModel):
    log_id: str
    ticket_id: str | None
    model: str
    prompt_version: str
    prompt: str
    response: str
    parsed_json: dict[str, Any] | None
    confidence: float | None
    input_tokens: int | None
    output_tokens: int | None
    success: bool
    error_message: str | None
    execution_time_ms: int | None
    created_at: str


class PaginatedAILogResponse(BaseModel):
    items: list[AILogResponse]
    total: int
    offset: int
    limit: int


class AILogStatsResponse(BaseModel):
    total_interactions: int
    successful_interactions: int
    failed_interactions: int
    success_rate: float
    avg_execution_time_ms: float
    avg_confidence: float
    total_input_tokens: int
    total_output_tokens: int
    model_counts: dict[str, int]


def _log_to_response(log: Any) -> AILogResponse:
    return AILogResponse(
        log_id=str(log.log_id),
        ticket_id=str(log.ticket_id) if log.ticket_id else None,
        model=log.model,
        prompt_version=log.prompt_version,
        prompt=log.prompt,
        response=log.response,
        parsed_json=log.parsed_json,
        confidence=log.confidence,
        input_tokens=log.input_tokens,
        output_tokens=log.output_tokens,
        success=log.success,
        error_message=log.error_message,
        execution_time_ms=log.execution_time_ms,
        created_at=log.created_at.isoformat(),
    )


@router.get("", response_model=PaginatedAILogResponse)
async def list_ai_logs(
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    model: str | None = Query(None),
    prompt_version: str | None = Query(None),
    success: bool | None = Query(None),
    date_from: datetime | None = Query(None),
    date_to: datetime | None = Query(None),
    db: AsyncSession = Depends(get_db),
) -> PaginatedAILogResponse:
    repo = AILogRepository(db)
    logs = await repo.list_logs(
        offset=offset,
        limit=limit,
        model=model,
        prompt_version=prompt_version,
        success=success,
        date_from=date_from,
        date_to=date_to,
    )
    total = await repo.count_logs(
        model=model,
        prompt_version=prompt_version,
        success=success,
        date_from=date_from,
        date_to=date_to,
    )
    return PaginatedAILogResponse(
        items=[_log_to_response(log) for log in logs],
        total=total,
        offset=offset,
        limit=limit,
    )


@router.get("/stats", response_model=AILogStatsResponse)
async def get_ai_log_stats(
    db: AsyncSession = Depends(get_db),
) -> AILogStatsResponse:
    repo = AILogRepository(db)
    stats = await repo.get_stats()
    return AILogStatsResponse(**stats)


@router.get("/{ticket_id}", response_model=list[AILogResponse])
async def get_ai_logs_by_ticket(
    ticket_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> list[AILogResponse]:
    repo = AILogRepository(db)
    logs = await repo.get_by_ticket_id(ticket_id)
    return [_log_to_response(log) for log in logs]
