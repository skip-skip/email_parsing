from __future__ import annotations

from datetime import datetime
from typing import Any

from fastapi import APIRouter, Query
from pydantic import BaseModel

from backend.app.services.logging import (
    APP_LOG_FILE,
    REQUEST_LOG_FILE,
    count_log_entries,
    read_log_entries,
)

router = APIRouter(prefix="/api/logs", tags=["logs"])


class LogEntry(BaseModel):
    timestamp: str
    level: str
    message: str
    module: str
    function: str
    line: int
    request_id: str


class PaginatedLogResponse(BaseModel):
    items: list[LogEntry]
    total: int
    offset: int
    limit: int


class LogStatsResponse(BaseModel):
    total_entries: int
    entries_by_level: dict[str, int]


def _count_by_level(log_file: Any) -> dict[str, int]:
    counts: dict[str, int] = {}
    if not log_file.exists():
        return counts

    import json

    with open(log_file, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
            except json.JSONDecodeError:
                continue

            record = entry.get("record", entry)
            entry_level = record.get("level", {})
            level_name = (
                entry_level.get("name", "INFO")
                if isinstance(entry_level, dict)
                else str(entry_level)
            )
            counts[level_name] = counts.get(level_name, 0) + 1

    return counts


@router.get("/app", response_model=PaginatedLogResponse)
async def list_app_logs(
    offset: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    level: str | None = Query(None, description="Filter by log level"),
    search: str | None = Query(None, description="Search in log messages"),
    request_id: str | None = Query(None, description="Filter by request ID"),
    date_from: datetime | None = Query(None, description="Start of date range"),
    date_to: datetime | None = Query(None, description="End of date range"),
) -> PaginatedLogResponse:
    entries = read_log_entries(
        log_file=APP_LOG_FILE,
        level=level,
        limit=limit,
        offset=offset,
        search=search,
        request_id=request_id,
        date_from=date_from,
        date_to=date_to,
    )
    total = count_log_entries(
        log_file=APP_LOG_FILE,
        level=level,
        search=search,
        request_id=request_id,
        date_from=date_from,
        date_to=date_to,
    )
    return PaginatedLogResponse(
        items=[LogEntry(**e) for e in entries],
        total=total,
        offset=offset,
        limit=limit,
    )


@router.get("/requests", response_model=PaginatedLogResponse)
async def list_request_logs(
    offset: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    level: str | None = Query(None, description="Filter by log level"),
    search: str | None = Query(None, description="Search in log messages"),
    request_id: str | None = Query(None, description="Filter by request ID"),
    date_from: datetime | None = Query(None, description="Start of date range"),
    date_to: datetime | None = Query(None, description="End of date range"),
) -> PaginatedLogResponse:
    entries = read_log_entries(
        log_file=REQUEST_LOG_FILE,
        level=level,
        limit=limit,
        offset=offset,
        search=search,
        request_id=request_id,
        date_from=date_from,
        date_to=date_to,
    )
    total = count_log_entries(
        log_file=REQUEST_LOG_FILE,
        level=level,
        search=search,
        request_id=request_id,
        date_from=date_from,
        date_to=date_to,
    )
    return PaginatedLogResponse(
        items=[LogEntry(**e) for e in entries],
        total=total,
        offset=offset,
        limit=limit,
    )


@router.get("/stats", response_model=LogStatsResponse)
async def get_log_stats() -> LogStatsResponse:
    app_counts = _count_by_level(APP_LOG_FILE)
    request_counts = _count_by_level(REQUEST_LOG_FILE)

    merged: dict[str, int] = {}
    for level_name, count in app_counts.items():
        merged[level_name] = merged.get(level_name, 0) + count
    for level_name, count in request_counts.items():
        merged[level_name] = merged.get(level_name, 0) + count

    total = sum(merged.values())
    return LogStatsResponse(
        total_entries=total,
        entries_by_level=merged,
    )
