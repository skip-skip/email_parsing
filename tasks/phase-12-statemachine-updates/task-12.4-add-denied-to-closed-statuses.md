# Task 12.4 -- Add DENIED to CLOSED_STATUSES + Clean Up Phantom Statuses

## Status
Not Started

## Description
Add DENIED to CLOSED_STATUSES and remove phantom statuses ("DECLINED", "CANCELLED") that don't exist in the TicketStatus enum. This ensures denied tickets appear in the Closed Tasks view.

## Files to Modify
- `backend/app/api/tickets.py:167` -- Update CLOSED_STATUSES tuple

## Implementation Details

### tickets.py
Change line 167 from:
```python
CLOSED_STATUSES = ("COMPLETED", "DECLINED", "CANCELLED")
```
To:
```python
CLOSED_STATUSES = ("COMPLETED", "DENIED", "ARCHIVED")
```

Rationale:
- "DECLINED" and "CANCELLED" don't exist in TicketStatus enum -- they are phantom strings
- "DENIED" is the new terminal status for schedule decline
- "ARCHIVED" should be visible in closed view (currently invisible in all views)

## Acceptance Criteria
- CLOSED_STATUSES contains "COMPLETED", "DENIED", "ARCHIVED"
- CLOSED_STATUSES does not contain "DECLINED" or "CANCELLED"
- Tickets with status DENIED appear in GET /api/tickets/closed response
- Tickets with status ARCHIVED appear in GET /api/tickets/closed response

## Testing
- Verify CLOSED_STATUSES tuple contains the correct statuses
- Run existing tests to ensure no regressions
