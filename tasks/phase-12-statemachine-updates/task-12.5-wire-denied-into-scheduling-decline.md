# Task 12.5 -- Wire DENIED into Scheduling Queue Decline Path

## Status
Not Started

## Description
Change the scheduling queue decline action to transition the ticket to DENIED instead of WAITING_FOR_INFORMATION. This makes the decline action terminal rather than re-entering the missing info flow.

## Files to Modify
- `backend/app/services/queues/scheduling_queue.py:215` -- Change transition target

## Implementation Details

### scheduling_queue.py
Change line 215 from:
```python
await transition_ticket(ticket_uuid, TicketStatus.WAITING_FOR_INFORMATION, strict_mode=False)
```
To:
```python
await transition_ticket(ticket_uuid, TicketStatus.DENIED, strict_mode=False)
```

Also remove the follow-up draft creation and missing info queue addition (lines 222-242) since the ticket is now in a terminal state.

## Acceptance Criteria
- Scheduling queue decline transitions ticket to DENIED
- No follow-up draft is created on decline
- Ticket is not added to missing info queue on decline
- Queue record status is set to "DECLINED"

## Testing
- Verify decline_schedule transitions ticket to DENIED
- Verify no MissingInfoQueueRecord is created on decline
- Run existing tests to ensure no regressions
