from __future__ import annotations

import asyncio
import logging
from datetime import datetime
from typing import Any

from backend.app.workflows.states import WorkflowState

logger = logging.getLogger(__name__)


def plan_schedule(state: WorkflowState) -> dict[str, Any]:
    logger.info("Planning schedule for ticket %s", state["ticket_id"])
    parsed = state.get("parsed_data") or {}

    deadline_str = parsed.get("deadline")
    budget_hours = parsed.get("budget_hours", 0)
    task_description = parsed.get("task_description", "")

    if not deadline_str or not budget_hours:
        logger.warning(
            "Missing deadline or budget_hours for ticket %s, returning empty schedule",
            state["ticket_id"],
        )
        return {
            "status": "READY_FOR_SCHEDULING",
            "schedule_blocks": [],
        }

    try:
        deadline = datetime.fromisoformat(deadline_str)
    except (ValueError, TypeError):
        logger.warning("Invalid deadline format: %s", deadline_str)
        return {
            "status": "READY_FOR_SCHEDULING",
            "schedule_blocks": [],
        }

    from backend.app.agents.calendar_planning_agent import CalendarPlanningAgent

    agent = CalendarPlanningAgent()
    suggestion = asyncio.run(
        agent.suggest_schedule(
            ticket_id=state["ticket_id"],
            deadline=deadline,
            budget_hours=float(budget_hours),
            task_description=task_description or "",
        )
    )

    blocks = [
        {
            "start_time": b.start_time.isoformat(),
            "end_time": b.end_time.isoformat(),
            "hours": b.hours,
            "description": b.description,
        }
        for b in suggestion.blocks
    ]

    return {
        "status": "READY_FOR_SCHEDULING",
        "schedule_blocks": blocks,
    }
