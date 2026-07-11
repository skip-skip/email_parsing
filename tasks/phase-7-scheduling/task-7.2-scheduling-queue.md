# Task 7.2 — Build Scheduling Queue Service

## Description
Create the service that manages the scheduling review queue.

## Status
Not Started

## Subtasks
- Create `backend/app/services/queues/scheduling_queue.py`:
  - `add_to_queue(ticket_id, suggestion) -> QueueItem`
  - `get_queue() -> list[QueueItem]`
  - `approve_schedule(ticket_id, selected_blocks) -> None`
  - `modify_schedule(ticket_id, modified_blocks) -> None`
  - `decline_schedule(ticket_id, reason=None) -> None`
- Create `scheduling_queue_item.py` model:
  - `ticket_id: UUID`
  - `ticket: Ticket`
  - `suggestion: ScheduleSuggestion`
  - `calendar_events: list[CalendarEvent]`
  - `status: str`

## Dependencies
- Task 7.1
- Task 5.1
- Task 2.6

## Acceptance Criteria
- Tickets are added to queue with suggestions
- Queue returns all pending items with full context
- Approval creates calendar events
- Decline sends decline email
- Modification updates blocks for re-approval
