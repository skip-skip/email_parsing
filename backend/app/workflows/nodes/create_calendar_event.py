from __future__ import annotations

import logging
from typing import Any

from backend.app.workflows.states import WorkflowState

logger = logging.getLogger(__name__)


def create_calendar_event(state: WorkflowState) -> dict[str, Any]:
    logger.info("Creating calendar event for ticket %s", state["ticket_id"])
    return {
        "status": "CALENDAR_CREATED",
        "calendar_event_id": f"evt-{state['ticket_id']}",
    }
