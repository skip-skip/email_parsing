# Task 12.1 -- Add DENIED Status to TicketStatus Enum

## Status
Not Started

## Description
Add a new DENIED terminal status to the TicketStatus enum. This status will be used when a schedule is declined, replacing the current behavior of re-entering WAITING_FOR_INFORMATION.

## Files to Modify
- `backend/app/workflows/states.py:17-29` -- Add `DENIED = "DENIED"` to enum
- `backend/app/workflows/transitions.py:13-26` -- Add `TicketStatus.DENIED: []` as terminal state

## Implementation Details

### states.py
Add `DENIED = "DENIED"` after ARCHIVED in the TicketStatus enum.

### transitions.py
Add `TicketStatus.DENIED: []` to VALID_TRANSITIONS dict. This makes DENIED a terminal state with no outgoing transitions.

## Acceptance Criteria
- `TicketStatus.DENIED` exists and equals `"DENIED"`
- `VALID_TRANSITIONS[TicketStatus.DENIED]` is an empty list
- `can_transition(TicketStatus.DENIED, any_status)` returns False for all statuses

## Testing
- Verify `TicketStatus("DENIED")` returns `TicketStatus.DENIED`
- Verify `can_transition(TicketStatus.DENIED, TicketStatus.COMPLETED)` returns False
- Run existing tests to ensure no regressions
