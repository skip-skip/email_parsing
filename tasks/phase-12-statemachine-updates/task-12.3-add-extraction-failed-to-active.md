# Task 12.3 -- Add EXTRACTION_FAILED to ACTIVE_STATUSES

## Status
Not Started

## Description
Add EXTRACTION_FAILED to ACTIVE_STATUSES so that tickets in this state are visible in the Active Tasks UI view. Currently, EXTRACTION_FAILED tickets are invisible in all views.

## Files to Modify
- `backend/app/api/tickets.py:21` -- Add "EXTRACTION_FAILED" to ACTIVE_STATUSES tuple

## Implementation Details

### tickets.py
Change line 21 from:
```python
ACTIVE_STATUSES = ("NEW", "ACCEPTED", "CALENDAR_CREATED", "IN_PROGRESS", "WAITING_FOR_INFORMATION", "AWAITING_REPLY")
```
To:
```python
ACTIVE_STATUSES = ("NEW", "ACCEPTED", "CALENDAR_CREATED", "IN_PROGRESS", "WAITING_FOR_INFORMATION", "AWAITING_REPLY", "EXTRACTION_FAILED")
```

## Acceptance Criteria
- ACTIVE_STATUSES includes "EXTRACTION_FAILED"
- Tickets with status EXTRACTION_FAILED appear in GET /api/tickets/active response

## Testing
- Verify ACTIVE_STATUSES tuple contains "EXTRACTION_FAILED"
- Run existing tests to ensure no regressions
