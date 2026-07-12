# Task 4.5 — Build Conversation Tracker

## Description
Create the agent that merges new reply information into existing tickets.

## Status
Complete

## Subtasks
- Create `conversation_tracker.py`:
  - Accept new email and existing ticket
  - Re-parse the new email with context of previous emails in thread
  - Merge new fields into ticket:
    - If new field is non-null and old was null → replace
    - If new field differs from old → update with latest
    - Preserve history of changes
  - Update ticket `updated_at` timestamp
  - Return merge summary (which fields changed)
- Create `merge_result.py`:
  - `ticket_id: UUID`
  - `updated_fields: list[str]`
  - `previous_values: dict[str, Any]`
  - `new_values: dict[str, Any]`
- Add conversation context to parsing prompt:
  - Include previous emails in thread
  - Instruct model to extract only new/updated information

## Dependencies
- Task 4.4
- Task 2.6

## Acceptance Criteria
- New replies update existing tickets
- Field history is preserved
- Only non-null new values overwrite existing
- Merge summary tracks all changes
- Parsing uses conversation context
