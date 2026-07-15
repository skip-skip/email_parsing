# Task 12.2 -- Remove PENDING_USER_APPROVAL from Transition Map

## Status
Not Started

## Description
Remove PENDING_USER_APPROVAL from VALID_TRANSITIONS. This status is in the transition map but no code path reaches it -- the scheduling queue approve path jumps directly from READY_FOR_SCHEDULING to IN_PROGRESS (strict_mode=False).

## Files to Modify
- `backend/app/workflows/transitions.py:19-20` -- Remove two entries

## Implementation Details

### transitions.py
Remove these two lines from VALID_TRANSITIONS:
```python
TicketStatus.READY_FOR_SCHEDULING: [TicketStatus.PENDING_USER_APPROVAL],
TicketStatus.PENDING_USER_APPROVAL: [TicketStatus.ACCEPTED, TicketStatus.WAITING_FOR_INFORMATION],
```

Keep PENDING_USER_APPROVAL in the TicketStatus enum for backward compatibility (existing database records may reference it).

## Acceptance Criteria
- `VALID_TRANSITIONS` does not contain READY_FOR_SCHEDULING or PENDING_USER_APPROVAL as keys
- `can_transition(TicketStatus.READY_FOR_SCHEDULING, TicketStatus.PENDING_USER_APPROVAL)` returns False
- `can_transition(TicketStatus.PENDING_USER_APPROVAL, TicketStatus.ACCEPTED)` returns False
- PENDING_USER_APPROVAL still exists in TicketStatus enum (backward compat)

## Testing
- Verify transition map no longer contains the removed entries
- Run existing tests to ensure no regressions
