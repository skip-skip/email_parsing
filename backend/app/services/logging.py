import json
import os
import sys
import time
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import loguru
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

SLOW_REQUEST_THRESHOLD_MS: float = 500.0
LOG_DIR = Path("logs")
APP_LOG_FILE = LOG_DIR / "app.log"
REQUEST_LOG_FILE = LOG_DIR / "requests.log"


def setup_logging() -> None:
    """Configure structured logging with Loguru."""
    log_level = os.environ.get("LOG_LEVEL", "INFO").upper()

    loguru.logger.remove()

    loguru.logger.add(
        sys.stderr,
        level=log_level,
        format=(
            "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{extra[request_id]}</cyan> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> — "
            "<level>{message}</level>"
        ),
        colorize=True,
        backtrace=True,
        diagnose=True,
    )

    os.makedirs(LOG_DIR, exist_ok=True)

    loguru.logger.add(
        str(APP_LOG_FILE),
        level=log_level,
        format=(
            "{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | "
            "{extra[request_id]} | {name}:{function}:{line} — {message}"
        ),
        rotation="00:00",
        retention=30,
        compression="gz",
        serialize=True,
        backtrace=True,
        diagnose=True,
    )

    loguru.logger.add(
        str(REQUEST_LOG_FILE),
        level="INFO",
        format="{message}",
        rotation="00:00",
        retention=30,
        compression="gz",
        serialize=True,
        filter=lambda record: record["extra"].get("is_request", False),
    )

    def _default_request_id(record: Any) -> None:
        record["extra"].setdefault("request_id", "startup")
        record["extra"].setdefault("is_request", False)

    loguru.logger.configure(patcher=_default_request_id)


def read_log_entries(
    log_file: Path,
    level: str | None = None,
    limit: int = 100,
    offset: int = 0,
    search: str | None = None,
    request_id: str | None = None,
    date_from: datetime | None = None,
    date_to: datetime | None = None,
) -> list[dict[str, Any]]:
    """Read and filter log entries from a serialized log file."""
    entries: list[dict[str, Any]] = []

    if not log_file.exists():
        return entries

    level_order = {
        "TRACE": 5,
        "DEBUG": 10,
        "INFO": 20,
        "SUCCESS": 25,
        "WARNING": 30,
        "ERROR": 40,
        "CRITICAL": 50,
    }

    min_level = level_order.get(level.upper(), 0) if level else 0

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
            text = record.get("text", "")
            if isinstance(text, dict):
                text = text.get("message", "")

            message = record.get("message", text)
            if isinstance(message, dict):
                message = message.get("text", str(message))

            entry_level = record.get("level", {})
            level_name = (
                entry_level.get("name", "INFO")
                if isinstance(entry_level, dict)
                else str(entry_level)
            )

            if min_level > 0 and level_order.get(level_name, 0) < min_level:
                continue

            extra = record.get("exception", None)
            if isinstance(extra, dict) and extra.get("type") is not None:
                pass

            extra_data: dict[str, Any] = {}
            if isinstance(record.get("extra"), dict):
                extra_data = record["extra"]

            if request_id and extra_data.get("request_id") != request_id:
                continue

            combined_message = str(message)
            if search and search.lower() not in combined_message.lower():
                continue

            timestamp = record.get("time", {})
            if isinstance(timestamp, dict):
                timestamp_str = timestamp.get("timestamp", 0)
                try:
                    ts = datetime.fromtimestamp(float(timestamp_str), tz=UTC)
                except (ValueError, TypeError, OSError):
                    ts = datetime.now(tz=UTC)
            else:
                ts = datetime.now(tz=UTC)

            if date_from and ts < date_from:
                continue
            if date_to and ts > date_to:
                continue

            entries.append(
                {
                    "timestamp": ts.isoformat(),
                    "level": level_name,
                    "message": combined_message,
                    "module": record.get("name", ""),
                    "function": record.get("function", ""),
                    "line": record.get("line", 0),
                    "request_id": extra_data.get("request_id", ""),
                }
            )

    entries.sort(key=lambda e: e["timestamp"], reverse=True)
    return entries[offset : offset + limit]


def count_log_entries(
    log_file: Path,
    level: str | None = None,
    search: str | None = None,
    request_id: str | None = None,
    date_from: datetime | None = None,
    date_to: datetime | None = None,
) -> int:
    """Count log entries matching the given filters."""
    if not log_file.exists():
        return 0

    level_order = {
        "TRACE": 5,
        "DEBUG": 10,
        "INFO": 20,
        "SUCCESS": 25,
        "WARNING": 30,
        "ERROR": 40,
        "CRITICAL": 50,
    }

    min_level = level_order.get(level.upper(), 0) if level else 0
    count = 0

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
            text = record.get("text", "")
            if isinstance(text, dict):
                text = text.get("message", "")

            message = record.get("message", text)
            if isinstance(message, dict):
                message = message.get("text", str(message))

            entry_level = record.get("level", {})
            level_name = (
                entry_level.get("name", "INFO")
                if isinstance(entry_level, dict)
                else str(entry_level)
            )

            if min_level > 0 and level_order.get(level_name, 0) < min_level:
                continue

            extra_data: dict[str, Any] = {}
            if isinstance(record.get("extra"), dict):
                extra_data = record["extra"]

            if request_id and extra_data.get("request_id") != request_id:
                continue

            combined_message = str(message)
            if search and search.lower() not in combined_message.lower():
                continue

            timestamp = record.get("time", {})
            if isinstance(timestamp, dict):
                timestamp_str = timestamp.get("timestamp", 0)
                try:
                    ts = datetime.fromtimestamp(float(timestamp_str), tz=UTC)
                except (ValueError, TypeError, OSError):
                    ts = datetime.now(tz=UTC)
            else:
                ts = datetime.now(tz=UTC)

            if date_from and ts < date_from:
                continue
            if date_to and ts > date_to:
                continue

            count += 1

    return count


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Middleware that injects a unique request ID and logs request performance."""

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        request_id = request.headers.get("X-Request-ID") or uuid.uuid4().hex
        with loguru.logger.contextualize(
            request_id=request_id, is_request=True
        ):
            start_time = time.perf_counter()
            loguru.logger.info(
                "Request started: {} {}",
                request.method,
                request.url.path,
            )
            response = await call_next(request)
            elapsed_ms = (time.perf_counter() - start_time) * 1000

            if elapsed_ms > SLOW_REQUEST_THRESHOLD_MS:
                loguru.logger.warning(
                    "Slow request: {} {} -> {} ({:.0f}ms)",
                    request.method,
                    request.url.path,
                    response.status_code,
                    elapsed_ms,
                )
            else:
                loguru.logger.info(
                    "Request completed: {} {} -> {} ({:.0f}ms)",
                    request.method,
                    request.url.path,
                    response.status_code,
                    elapsed_ms,
                )

        response.headers["X-Request-ID"] = request_id
        response.headers["X-Response-Time"] = f"{elapsed_ms:.2f}ms"
        return response
