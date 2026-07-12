# Task 7.4 — Build Calendar Manager

## Description
Create the service that actually creates Outlook calendar events after approval.

## Status
Complete

## Subtasks
- Create `backend/app/services/scheduler/calendar_manager.py`:
  - `create_events(ticket_id, blocks) -> list[CalendarEvent]`
  - `update_events(ticket_id, new_blocks) -> list[CalendarEvent]`
  - `cancel_events(ticket_id) -> None`
- Handle edge cases:
  - Timezone conversion
  - All-day events
  - Overlapping blocks (merge or reject)

## Dependencies
- Task 3.3
- Task 2.6

## Acceptance Criteria
- Creates Outlook events after approval
- Events are linked to tickets in database
- Events can be updated or cancelled
- Timezone handling is correct
