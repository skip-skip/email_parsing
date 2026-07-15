from __future__ import annotations

import logging
from typing import Any

from backend.app.workflows.states import WorkflowState

logger = logging.getLogger(__name__)


def extraction_failed(state: WorkflowState) -> dict[str, Any]:
    """Terminal node for when extraction fails with low confidence.

    Logs the failure and returns a terminal state without generating
    any follow-up emails to the sender.
    """
    error = state.get("error", "Unknown extraction error")
    logger.error(
        "Extraction failed for ticket %s: %s",
        state["ticket_id"],
        error,
    )
    return {
        "status": "EXTRACTION_FAILED",
        "error": error,
    }
