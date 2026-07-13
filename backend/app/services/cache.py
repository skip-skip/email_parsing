"""Simple in-memory TTL cache for API responses and query results."""

from __future__ import annotations

import hashlib
import json
import time
from collections.abc import Callable
from typing import Any, TypeVar

T = TypeVar("T")

_DEFAULT_TTL_SECONDS = 60


class TTLCache:
    """Thread-safe in-memory cache with per-key TTL expiration."""

    def __init__(self, default_ttl: float = _DEFAULT_TTL_SECONDS) -> None:
        self._store: dict[str, tuple[Any, float]] = {}
        self._default_ttl = default_ttl

    def get(self, key: str) -> Any | None:
        entry = self._store.get(key)
        if entry is None:
            return None
        value, expires_at = entry
        if time.monotonic() > expires_at:
            del self._store[key]
            return None
        return value

    def set(self, key: str, value: Any, ttl: float | None = None) -> None:
        expires_at = time.monotonic() + (ttl if ttl is not None else self._default_ttl)
        self._store[key] = (value, expires_at)

    def invalidate(self, key: str) -> None:
        self._store.pop(key, None)

    def clear(self) -> None:
        self._store.clear()

    def prune(self) -> int:
        """Remove expired entries. Returns the number of entries removed."""
        now = time.monotonic()
        expired = [k for k, (_, exp) in self._store.items() if now > exp]
        for k in expired:
            del self._store[k]
        return len(expired)


def make_cache_key(*parts: Any) -> str:
    raw = json.dumps(parts, sort_keys=True, default=str)
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


query_cache = TTLCache(default_ttl=30.0)


def cached(
    ttl: float | None = None,
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Decorator that caches async function results keyed by arguments."""

    def decorator(fn: Callable[..., Any]) -> Callable[..., Any]:
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            key = make_cache_key(fn.__qualname__, args, sorted(kwargs.items()))
            hit = query_cache.get(key)
            if hit is not None:
                return hit
            result = await fn(*args, **kwargs)
            query_cache.set(key, result, ttl=ttl)
            return result

        wrapper.__name__ = fn.__name__
        wrapper.__doc__ = fn.__doc__
        return wrapper

    return decorator
