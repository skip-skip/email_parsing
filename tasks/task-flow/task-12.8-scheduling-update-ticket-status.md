# Task 12.8 — Scheduling Queue: Update Ticket Status on Approve/Decline

## Description
The scheduling queue currently updates its own record status but never transitions the ticket's status in the state machine. When a schedule is approved, the ticket should transition through ACCEPTED → CALENDAR_CREATED → IN_PROGRESS. When declined, the ticket should transition back to a state that allows re-scheduling or closure.

## Status
Not Started

## Subtasks
- Update `SchedulingQueue.approve_schedule()` (`backend/app/services/queues/scheduling_queue.py`):
  - After creating calendar events, call `transition_ticket(ticket_id, TicketStatus.ACCEPTED)` then `transition_ticket(ticket_id, TicketStatus.CALENDAR_CREATED)`
  - This moves the ticket from `READY_FOR_SCHEDULING` or `PENDING_USER_APPROVAL` to `CALENDAR_CREATED`
  - The ticket will then appear on the Active Tasks page (CALENDAR_CREATED is in ACTIVE_STATUSES)
- Update `SchedulingQueue.decline_schedule()`:
  - Call `transition_ticket(ticket_id, TicketStatus.WAITING_FOR_INFORMATION)` to move the ticket back to waiting state
  - This allows the ticket to be re-scheduled later or have different information gathered
  - Add `WAITING_FOR_INFORMATION` as a valid transition from `PENDING_USER_APPROVAL` if not already there (check `transitions.py`)
- Ensure `VALID_TRANSITIONS` in `transitions.py` includes:
  - `PENDING_USER_APPROVAL -> ACCEPTED` (should already exist)
  - `ACCEPTED -> CALENDAR_CREATED` (should already exist)
  - `PENDING_USER_APPROVAL -> WAITING_FOR_INFORMATION` (verify or add)
- Write unit tests:
  - `approve_schedule()` transitions ticket to CALENDAR_CREATED
  - `decline_schedule()` transitions ticket to WAITING_FOR_INFORMATION
  - Invalid transition is handled gracefully (logged, not raised)

## Dependencies
- Task 12.7 (calendar events must be created before status transitions)

## Acceptance Criteria
- Approving a schedule transitions the ticket to CALENDAR_CREATED
- Declining a schedule transitions the ticket to WAITING_FOR_INFORMATION
- Tickets with CALENDAR_CREATED status appear on the Active Tasks page
- State machine transitions are valid and logged
- All existing tests pass
