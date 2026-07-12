# Task 5.1 — Define Ticket State Machine

## Description
Create the state machine that governs all ticket transitions.

## Status
Complete

## Subtasks
- Create `backend/app/workflows/` directory
- Create `states.py` with `TicketStatus` enum:
  - `NEW`
  - `PARSED`
  - `VALIDATED`
  - `WAITING_FOR_INFORMATION`
  - `READY_FOR_SCHEDULING`
  - `PENDING_USER_APPROVAL`
  - `ACCEPTED`
  - `CALENDAR_CREATED`
  - `IN_PROGRESS`
  - `COMPLETED`
  - `ARCHIVED`
- Create `transitions.py` with transition rules:
  - Define valid transitions as a dict
  - Implement `can_transition(current, target) -> bool`
  - Implement `get_valid_transitions(current) -> list[TicketStatus]`
  - Raise `InvalidTransitionError` for illegal transitions
- Create `state_manager.py`:
  - `transition_ticket(ticket_id, target_status) -> Ticket`
  - Updates status and `updated_at` in database
  - Logs transition to AILog table
  - Returns updated ticket

## Dependencies
- Task 2.1
- Task 2.6

## Acceptance Criteria
- All lifecycle states are defined
- Invalid transitions are rejected with clear error
- Transitions are logged
- Database status stays in sync
