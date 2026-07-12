from __future__ import annotations

import logging
from typing import Any

from backend.app.workflows.states import WorkflowState

logger = logging.getLogger(__name__)


def plan_schedule(state: WorkflowState) -> dict[str, Any]:
    logger.info("Planning schedule for ticket %s", state["ticket_id"])
    parsed = state.get("parsed_data") or {}
    blocks = []
    if parsed.get("deadline"):
        blocks.append({
            "type": "deadline",
            "date": parsed["deadline"],
            "hours": parsed.get("budget_hours", 0),
        })
    return {
        "status": "READY_FOR_SCHEDULING",
        "schedule_blocks": blocks,
    }
