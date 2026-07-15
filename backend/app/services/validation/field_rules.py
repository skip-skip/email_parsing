from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass
class FieldRule:
    name: str
    required: bool = True
    min_length: int | None = None
    min_value: float | None = None
    max_value: float | None = None
    custom_validator: Callable[[Any], bool] | None = None
    error_message: str = ""


def _validate_task_description(value: Any) -> bool:
    if not isinstance(value, str):
        return False
    return len(value.strip()) >= 10


def _validate_project_number(value: Any) -> bool:
    if not isinstance(value, str):
        return False
    return len(value.strip()) > 0


def _validate_budget_hours(value: Any) -> bool:
    if value is None:
        return False
    try:
        return float(value) > 0
    except (ValueError, TypeError):
        return False


def _validate_deadline(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        try:
            value = datetime.fromisoformat(value)
        except ValueError:
            return False
    if isinstance(value, datetime):
        return True
    return False


DEFAULT_FIELD_RULES: list[FieldRule] = [
    FieldRule(
        name="task_description",
        required=True,
        custom_validator=_validate_task_description,
        error_message="Task description is required and must be at least 10 characters",
    ),
    FieldRule(
        name="project_number",
        required=True,
        custom_validator=_validate_project_number,
        error_message="Project number is required",
    ),
    FieldRule(
        name="budget_hours",
        required=False,
        custom_validator=_validate_budget_hours,
        error_message="Budget hours must be greater than 0",
    ),
    FieldRule(
        name="deadline",
        required=False,
        custom_validator=_validate_deadline,
        error_message="Deadline must be a valid date",
    ),
]
