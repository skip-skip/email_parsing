# Task 2.6 — Database Repository Layer

## Description
Create repository classes for database operations.

## Status
Not Started

## Subtasks
- Create `backend/app/services/database/repositories/`
- Create `ticket_repository.py` with methods:
  - `get_by_id(ticket_id) -> Ticket | None`
  - `get_by_conversation_id(conversation_id) -> Ticket | None`
  - `get_by_status(status) -> list[Ticket]`
  - `create(ticket_data) -> Ticket`
  - `update(ticket_id, fields) -> Ticket`
  - `delete(ticket_id) -> None`
- Create `email_repository.py` with methods:
  - `get_by_entry_id(entry_id) -> Email | None`
  - `get_by_conversation_id(conversation_id) -> list[Email]`
  - `create(email_data) -> Email`
- Create `calendar_repository.py` with methods:
  - `get_by_ticket_id(ticket_id) -> list[CalendarEvent]`
  - `create(event_data) -> CalendarEvent`
  - `update(event_id, fields) -> CalendarEvent`
- Create `ai_log_repository.py` with methods:
  - `create(log_data) -> AILog`
  - `get_by_ticket_id(ticket_id) -> list[AILog]`

## Dependencies
- Task 2.1
- Task 2.2
- Task 2.3
- Task 2.4

## Acceptance Criteria
- All repository methods work with test database
- Async/await used throughout
- Proper session management (no leaked connections)
