from __future__ import annotations

import logging
from typing import Any

from backend.app.workflows.states import WorkflowState

logger = logging.getLogger(__name__)


def receive_email(state: WorkflowState) -> dict[str, Any]:
    logger.info("Receiving email for ticket %s", state["ticket_id"])
    return {"status": "NEW"}
