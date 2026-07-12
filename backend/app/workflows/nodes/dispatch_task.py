from __future__ import annotations

import logging
from typing import Any

from backend.app.workflows.states import WorkflowState

logger = logging.getLogger(__name__)


def dispatch_task(state: WorkflowState) -> dict[str, Any]:
    logger.info("Dispatching task for ticket %s", state["ticket_id"])
    return {"status": "IN_PROGRESS"}
