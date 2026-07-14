# Task 12.16 — Enforce State Machine in EmailProcessor

## Description
The `EmailProcessor._persist_ticket_status()` method writes status directly to the database via `ticket_repo.update_status()`, bypassing the state machine in `transitions.py`. This means invalid transitions are possible (e.g., jumping from `NEW` directly to `IN_PROGRESS`). Replace direct DB writes with `transition_ticket()` to enforce the state machine.

## Status
Not Started

## Subtasks
- Update `EmailProcessor._persist_ticket_status()` (`backend/app/services/email_processor.py`):
  - Replace `ticket_repo.update_status(ticket_id, status)` with `transition_ticket(ticket_id, new_status)`
  - `transition_ticket()` already validates the transition against `VALID_TRANSITIONS` and logs warnings for invalid transitions
  - If the transition is invalid, log a warning but still persist the status (don't block email processing)
  - The transition should be non-blocking — email processing must continue even if the state machine rejects a transition
- Add a `strict_mode` parameter to `transition_ticket()` (`backend/app/workflows/state_manager.py`):
  - When `strict_mode=False` (default): log warning but allow the transition
  - When `strict_mode=True`: raise `InvalidTransitionError` and don't persist
  - Use `strict_mode=False` in `EmailProcessor` for backward compatibility
- Add `WAITING_FOR_INFORMATION → READY_FOR_SCHEDULING` to `VALID_TRANSITIONS` (`backend/app/workflows/transitions.py`):
  - This transition is needed for the missing info reply flow (Task 12.4)
  - Also verify `PENDING_USER_APPROVAL → WAITING_FOR_INFORMATION` exists for the decline flow (Task 12.8)
- Write unit tests:
  - `_persist_ticket_status()` calls `transition_ticket()` instead of `update_status()`
  - Invalid transition is logged but not raised (non-strict mode)
  - Invalid transition raises error (strict mode)
  - `WAITING_FOR_INFORMATION → READY_FOR_SCHEDULING` is a valid transition
  - `PENDING_USER_APPROVAL → WAITING_FOR_INFORMATION` is a valid transition

## Dependencies
None

## Acceptance Criteria
- `EmailProcessor` uses `transition_ticket()` for all status changes
- Invalid transitions are logged as warnings
- `strict_mode` parameter allows controlling behavior
- State machine transitions are properly validated
- All existing tests pass
