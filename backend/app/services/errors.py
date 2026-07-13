from __future__ import annotations

import asyncio
import functools
import logging
import time
from collections.abc import Callable
from typing import Any, TypeVar

logger = logging.getLogger(__name__)

F = TypeVar("F", bound=Callable[..., Any])


class AppError(Exception):
    """Base exception for all application errors."""

    status_code: int = 500
    default_message: str = "An unexpected error occurred"

    def __init__(self, message: str | None = None, detail: Any = None) -> None:
        self.message = message or self.default_message
        self.detail = detail
        super().__init__(self.message)


class NotFoundError(AppError):
    """Resource not found."""

    status_code = 404
    default_message = "Resource not found"


class ValidationError(AppError):
    """Request validation failed."""

    status_code = 422
    default_message = "Validation error"


class ConflictError(AppError):
    """Resource state conflict."""

    status_code = 409
    default_message = "Resource conflict"


class AuthenticationError(AppError):
    """Authentication required or failed."""

    status_code = 401
    default_message = "Authentication required"


class PermissionError(AppError):
    """Insufficient permissions."""

    status_code = 403
    default_message = "Insufficient permissions"


class ExternalServiceError(AppError):
    """External service (Ollama, Outlook COM, etc.) returned an error."""

    status_code = 502
    default_message = "External service error"


class TransientError(AppError):
    """Temporary failure that may succeed on retry."""

    status_code = 503
    default_message = "Service temporarily unavailable"


class RateLimitError(AppError):
    """Rate limit exceeded."""

    status_code = 429
    default_message = "Rate limit exceeded"


def retry(
    max_retries: int = 3,
    delay: float = 1.0,
    backoff_factor: float = 2.0,
    exceptions: tuple[type[Exception], ...] = (TransientError,),
) -> Callable[[F], F]:
    """Decorator that retries a function on transient failures.

    Supports both sync and async callables. Uses exponential backoff
    between attempts.
    """

    def decorator(func: F) -> F:
        if asyncio.iscoroutinefunction(func):
            return _make_async_wrapper(func, max_retries, delay, backoff_factor, exceptions)  # type: ignore[return-value]
        return _make_sync_wrapper(func, max_retries, delay, backoff_factor, exceptions)  # type: ignore[return-value]

    return decorator


def _make_async_wrapper(
    func: Callable[..., Any],
    max_retries: int,
    delay: float,
    backoff_factor: float,
    exceptions: tuple[type[Exception], ...],
) -> Callable[..., Any]:
    @functools.wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> Any:
        last_exception: Exception | None = None
        current_delay = delay

        for attempt in range(max_retries + 1):
            try:
                return await func(*args, **kwargs)
            except exceptions as exc:
                last_exception = exc
                if attempt < max_retries:
                    logger.warning(
                        "Retry %d/%d for %s after %.1fs: %s",
                        attempt + 1,
                        max_retries,
                        func.__qualname__,
                        current_delay,
                        exc,
                    )
                    await asyncio.sleep(current_delay)
                    current_delay *= backoff_factor

        raise last_exception  # type: ignore[misc]

    return wrapper


def _make_sync_wrapper(
    func: Callable[..., Any],
    max_retries: int,
    delay: float,
    backoff_factor: float,
    exceptions: tuple[type[Exception], ...],
) -> Callable[..., Any]:
    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        last_exception: Exception | None = None
        current_delay = delay

        for attempt in range(max_retries + 1):
            try:
                return func(*args, **kwargs)
            except exceptions as exc:
                last_exception = exc
                if attempt < max_retries:
                    logger.warning(
                        "Retry %d/%d for %s after %.1fs: %s",
                        attempt + 1,
                        max_retries,
                        func.__qualname__,
                        current_delay,
                        exc,
                    )
                    time.sleep(current_delay)
                    current_delay *= backoff_factor

        raise last_exception  # type: ignore[misc]

    return wrapper
