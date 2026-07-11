# Task 2.3 — CalendarEvent Model

## Description
Create the CalendarEvent SQLAlchemy model.

## Status
Not Started

## Subtasks
- Create `backend/app/models/calendar_event.py`
- Define `CalendarEvent` model with columns:
  - `calendar_event_id` (UUID primary key, auto-generated)
  - `ticket_id` (UUID, foreign key to tickets)
  - `outlook_event_id` (String, nullable — set after creation)
  - `start_time` (DateTime)
  - `end_time` (DateTime)
  - `duration` (Float — hours)
  - `status` (String, default `PROPOSED`)
  - `created_at` (DateTime, server_default=now)
- Add relationship to Ticket

## Dependencies
- Task 1.5
- Task 2.1

## Acceptance Criteria
- Model compiles and maps correctly
- Migration creates table with foreign key
