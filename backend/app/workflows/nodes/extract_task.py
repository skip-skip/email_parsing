from __future__ import annotations

import asyncio
import logging
from typing import Any

from backend.app.workflows.states import WorkflowState

logger = logging.getLogger(__name__)


def extract_task(state: WorkflowState) -> dict[str, Any]:
    logger.info("Extracting task for ticket %s", state["ticket_id"])
    from backend.app.agents.email_parsing_agent import EmailParsingAgent

    agent = EmailParsingAgent()
    parsed = asyncio.run(
        agent.parse(
            sender=state.get("sender", ""),
            subject=state.get("subject", ""),
            body=state.get("body", ""),
            ticket_id=state["ticket_id"],
        )
    )
    return {
        "status": "PARSED",
        "parsed_data": {
            "client": parsed.client,
            "sender": parsed.sender,
            "subject": parsed.subject,
            "project_number": parsed.project_number,
            "task_description": parsed.task_description,
            "deadline": parsed.deadline.isoformat() if parsed.deadline else None,
            "budget_hours": parsed.budget_hours,
            "attachments": parsed.attachments,
            "confidence": parsed.confidence,
        },
    }
