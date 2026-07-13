from __future__ import annotations

import asyncio
from typing import Any

from fastapi import APIRouter

from backend.app.services.llm.model_manager import ModelManager

router = APIRouter(prefix="/api/llm", tags=["llm"])

_manager = ModelManager()


def get_model_manager() -> ModelManager:
    return _manager


@router.get("/health")
async def llm_health() -> dict[str, Any]:
    health = await asyncio.to_thread(_manager.check_health)
    return {
        "status": "healthy" if any(h.available for h in health.values()) else "degraded",
        "models": {
            model: {
                "available": status.available,
                "last_checked": status.last_checked.isoformat() if status.last_checked else None,
                "last_error": status.last_error,
            }
            for model, status in health.items()
        },
        "fallback_chain": _manager.fallback_chain,
        "usage_stats": {
            "total_requests": _manager.usage_stats.total_requests,
            "successful_requests": _manager.usage_stats.successful_requests,
            "failed_requests": _manager.usage_stats.failed_requests,
            "model_counts": _manager.usage_stats.model_counts,
            "model_switches": _manager.usage_stats.model_switches,
        },
    }
