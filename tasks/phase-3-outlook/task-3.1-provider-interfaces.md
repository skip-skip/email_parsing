# Task 3.1 — Define Provider Interfaces

## Description
Create abstract base classes that define the contract for Outlook operations.

## Status
Complete

## Subtasks
- Create `backend/app/services/outlook/` directory
- Create `base.py` with abstract classes:
  - `EmailProvider`:
    - `get_new_messages() -> list[EmailMessage]`
    - `get_conversation(conversation_id) -> list[EmailMessage]`
    - `send_reply(conversation_id, body) -> None`
    - `get_message_by_entry_id(entry_id) -> EmailMessage`
  - `CalendarProvider`:
    - `get_events(start, end) -> list[CalendarEvent]`
    - `get_free_busy(start, end) -> FreeBusyInfo`
    - `create_event(title, start, end, body) -> str` (returns event ID)
    - `update_event(event_id, fields) -> None`
    - `delete_event(event_id) -> None`
- Create `models.py` with Outlook-specific data models:
  - `EmailMessage` (dataclass/Pydantic)
  - `FreeBusyInfo`
  - `OutlookCalendarEvent`

## Dependencies
- Task 1.3

## Acceptance Criteria
- Interfaces define clear contracts
- Data models match shared schemas
- No COM imports in this module
