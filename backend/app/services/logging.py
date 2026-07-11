import os
import sys
import uuid
from typing import Any

import loguru
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response


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

    os.makedirs("logs", exist_ok=True)
    loguru.logger.add(
        "logs/app.log",
        level=log_level,
        format=(
            "{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | "
            "{extra[request_id]} | {name}:{function}:{line} — {message}"
        ),
        rotation="10 MB",
        retention=5,
        compression="gz",
        serialize=True,
        backtrace=True,
        diagnose=True,
    )

    def _default_request_id(record: Any) -> None:
        record["extra"].setdefault("request_id", "startup")

    loguru.logger.configure(patcher=_default_request_id)


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Middleware that injects a unique request ID into each request."""

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        request_id = request.headers.get("X-Request-ID") or uuid.uuid4().hex
        with loguru.logger.contextualize(request_id=request_id):
            loguru.logger.info(
                "Request started: {} {}", request.method, request.url.path
            )
            response = await call_next(request)
            loguru.logger.info(
                "Request completed: {} {} -> {}",
                request.method,
                request.url.path,
                response.status_code,
            )
        response.headers["X-Request-ID"] = request_id
        return response
