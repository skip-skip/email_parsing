from __future__ import annotations

from fastapi import APIRouter

from backend.app.services.cache import query_cache
from backend.app.services.metrics import get_metrics

router = APIRouter(prefix="/api/metrics", tags=["metrics"])


@router.get("")
async def get_server_metrics() -> dict[str, object]:
    return get_metrics()


@router.post("/cache/clear")
async def clear_cache() -> dict[str, str]:
    query_cache.clear()
    return {"status": "cache cleared"}
