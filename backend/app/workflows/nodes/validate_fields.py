from __future__ import annotations

import logging
from typing import Any

from backend.app.services.validation.validator import TicketValidator
from backend.app.workflows.states import TicketStatus, WorkflowState

logger = logging.getLogger(__name__)

_validator = TicketValidator()


def validate_fields(state: WorkflowState) -> dict[str, Any]:
    logger.info("Validating fields for ticket %s", state["ticket_id"])
    parsed = state.get("parsed_data") or {}
    result = _validator.validate(parsed)
    return {
        "status": TicketStatus.VALIDATED.value,
        "validation_result": {
            "is_valid": result.is_complete,
            "missing_fields": result.missing_fields,
            "field_status": result.field_status,
            "warnings": result.warnings,
        },
        "missing_fields": result.missing_fields,
    }
