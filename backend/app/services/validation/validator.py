from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from backend.app.services.validation.field_rules import (
    DEFAULT_FIELD_RULES,
    FieldRule,
)


@dataclass
class ValidationResult:
    is_complete: bool
    missing_fields: list[str]
    field_status: dict[str, bool]
    warnings: list[str] = field(default_factory=list)


class TicketValidator:
    def __init__(self, rules: list[FieldRule] | None = None) -> None:
        self._rules = rules or DEFAULT_FIELD_RULES

    def validate(self, parsed_data: dict[str, Any]) -> ValidationResult:
        missing_fields: list[str] = []
        field_status: dict[str, bool] = {}
        warnings: list[str] = []

        for rule in self._rules:
            value = parsed_data.get(rule.name)
            is_valid = self._validate_field(rule, value)
            field_status[rule.name] = is_valid

            if not is_valid:
                missing_fields.append(rule.name)

            if rule.name == "deadline" and value is not None:
                if self._is_past_deadline(value):
                    warnings.append(f"Deadline {value} is in the past")

        return ValidationResult(
            is_complete=len(missing_fields) == 0,
            missing_fields=missing_fields,
            field_status=field_status,
            warnings=warnings,
        )

    def _validate_field(self, rule: FieldRule, value: Any) -> bool:
        if rule.required and (value is None or value == ""):
            return False

        if rule.custom_validator is not None:
            return rule.custom_validator(value)

        if rule.min_length is not None and isinstance(value, str):
            if len(value.strip()) < rule.min_length:
                return False

        if rule.min_value is not None:
            try:
                if float(value) < rule.min_value:
                    return False
            except (ValueError, TypeError):
                return False

        if rule.max_value is not None:
            try:
                if float(value) > rule.max_value:
                    return False
            except (ValueError, TypeError):
                return False

        return True

    def _is_past_deadline(self, value: Any) -> bool:
        if isinstance(value, str):
            try:
                value = datetime.fromisoformat(value)
            except ValueError:
                return False
        if isinstance(value, datetime):
            return value < datetime.now()
        return False
