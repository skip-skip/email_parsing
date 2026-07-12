from __future__ import annotations

import logging
from typing import Any

from backend.app.workflows.states import WorkflowState

logger = logging.getLogger(__name__)


def draft_missing_info_email(state: WorkflowState) -> dict[str, Any]:
    logger.info("Drafting missing info email for ticket %s", state["ticket_id"])
    missing = state.get("missing_fields", [])
    draft = (
        f"Hello,\n\n"
        f"We need additional information for your request:\n"
        f"- Missing: {', '.join(missing)}\n\n"
        f"Please provide these details so we can proceed.\n"
    )
    return {
        "status": "WAITING_FOR_INFORMATION",
        "draft_email": draft,
    }
