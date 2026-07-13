"""Request metrics tracking and collection middleware."""

from __future__ import annotations

import time
from collections import deque

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

# Ring buffer of recent response times (max 1000 entries).
_response_times: deque[float] = deque(maxlen=1000)
_request_count: int = 0
_error_count: int = 0


def get_metrics() -> dict[str, object]:
    """Return current request metrics snapshot."""
    times = list(_response_times)
    avg_ms = (sum(times) / len(times)) if times else 0.0
    p95_ms = (
        sorted(times)[int(len(times) * 0.95)]
        if len(times) >= 2
        else (times[0] if times else 0.0)
    )
    p99_ms = (
        sorted(times)[int(len(times) * 0.99)]
        if len(times) >= 2
        else (times[0] if times else 0.0)
    )
    return {
        "total_requests": _request_count,
        "total_errors": _error_count,
        "error_rate": round(_error_count / _request_count * 100, 2)
        if _request_count > 0
        else 0.0,
        "avg_response_ms": round(avg_ms, 2),
        "p95_response_ms": round(p95_ms, 2),
        "p99_response_ms": round(p99_ms, 2),
        "sample_size": len(times),
    }


class MetricsMiddleware(BaseHTTPMiddleware):
    """Middleware that collects request count, error rate, and response time percentiles."""

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        global _request_count, _error_count
        start = time.perf_counter()
        response = await call_next(request)
        elapsed_ms = (time.perf_counter() - start) * 1000

        _request_count += 1
        _response_times.append(elapsed_ms)
        if response.status_code >= 500:
            _error_count += 1

        response.headers["X-Response-Time"] = f"{elapsed_ms:.2f}ms"
        return response
