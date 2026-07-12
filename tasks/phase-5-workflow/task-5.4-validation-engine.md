# Task 5.4 — Implement Validation Engine

## Description
Build the deterministic validation logic for ticket completeness.

## Status
Complete

## Subtasks
- Create `backend/app/services/validation/` directory
- Create `validator.py`:
  - Define required fields list
  - Implement `validate_ticket(parsed_data) -> ValidationResult`
  - `ValidationResult`:
    - `is_complete: bool`
    - `missing_fields: list[str]`
    - `field_status: dict[str, bool]`
  - Pure Python logic — no LLM calls
  - Handle edge cases:
    - Empty string = missing
    - Zero budget_hours = missing
    - Past deadline = warning (still valid)
- Create `field_rules.py`:
  - Define validation rules per field:
    - `task_description`: required, min length 10
    - `project_number`: required, format validation
    - `budget_hours`: required, must be > 0
    - `deadline`: required, must be future date
  - Allow custom rules per field

## Dependencies
- Task 1.3

## Acceptance Criteria
- Validates all required fields
- Returns clear list of missing fields
- No AI involvement — pure Python
- Handles edge cases (empty strings, zero values)
- Rules are configurable
