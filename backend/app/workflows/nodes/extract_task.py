from __future__ import annotations

import asyncio
import logging
from typing import Any

from backend.app.workflows.states import WorkflowState

logger = logging.getLogger(__name__)

LOW_CONFIDENCE_THRESHOLD = 0.3


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

    parsed_data = {
        "client": parsed.client,
        "sender": parsed.sender,
        "subject": parsed.subject,
        "project_number": parsed.project_number,
        "task_description": parsed.task_description,
        "deadline": parsed.deadline.isoformat() if parsed.deadline else None,
        "budget_hours": parsed.budget_hours,
        "attachments": parsed.attachments,
        "confidence": parsed.confidence,
    }

    if parsed.confidence < LOW_CONFIDENCE_THRESHOLD:
        logger.warning(
            "Low extraction confidence (%.2f < %.2f) for ticket %s, "
            "marking extraction as failed",
            parsed.confidence,
            LOW_CONFIDENCE_THRESHOLD,
            state["ticket_id"],
        )
        return {
            "status": "PARSED",
            "parsed_data": parsed_data,
            "error": f"Extraction confidence too low: {parsed.confidence}",
            "missing_fields": [],
        }

    return {
        "status": "PARSED",
        "parsed_data": parsed_data,
    }
