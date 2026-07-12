from __future__ import annotations

import logging
from typing import Any

from backend.app.workflows.states import WorkflowState

logger = logging.getLogger(__name__)

REQUIRED_FIELDS = ["task_description", "project_number", "budget_hours", "deadline"]


def validate_fields(state: WorkflowState) -> dict[str, Any]:
    logger.info("Validating fields for ticket %s", state["ticket_id"])
    parsed = state.get("parsed_data") or {}
    missing = [f for f in REQUIRED_FIELDS if not parsed.get(f)]
    validation_result = {
        "is_valid": len(missing) == 0,
        "missing_fields": missing,
    }
    return {
        "status": "VALIDATED",
        "validation_result": validation_result,
        "missing_fields": missing,
    }
