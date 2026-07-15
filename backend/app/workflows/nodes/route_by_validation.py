from __future__ import annotations

import logging

from backend.app.workflows.states import WorkflowState

logger = logging.getLogger(__name__)


def route_by_validation(state: WorkflowState) -> str:
    if state.get("error"):
        logger.warning(
            "Ticket %s has extraction error, routing to failed handler: %s",
            state["ticket_id"],
            state["error"],
        )
        return "extraction_failed"
    if state.get("missing_fields"):
        logger.info(
            "Ticket %s has missing fields, routing to draft email",
            state["ticket_id"],
        )
        return "draft_missing_info_email"
    logger.info("Ticket %s validated, routing to schedule", state["ticket_id"])
    return "plan_schedule"
