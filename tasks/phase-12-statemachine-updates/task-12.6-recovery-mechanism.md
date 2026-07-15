# Task 12.6 -- Add Recovery Mechanism for Ticket/Queue Status Drift

## Status
Not Started

## Description
Add a recovery mechanism to detect and fix orphaned tickets -- tickets in WAITING_FOR_INFORMATION or AWAITING_REPLY with no corresponding queue entry, or queue entries with mismatched ticket status.

## Files to Create
- `backend/app/services/recovery.py` -- New file with recovery functions

## Files to Modify
- `backend/app/api/tickets.py` -- Add health check endpoint that runs recovery

## Implementation Details

### recovery.py
Create functions:
1. `find_orphaned_tickets()` -- Find tickets in WAITING_FOR_INFORMATION/AWAITING_REPLY with no queue entry
2. `find_mismatched_queue_entries()` -- Find queue entries where ticket status doesn't match
3. `recover_orphaned_ticket(ticket_id)` -- Log the issue, optionally transition to a safe state

### Health Check Endpoint
Add GET /api/health/recovery that runs the detection functions and returns counts of issues found.

## Acceptance Criteria
- `find_orphaned_tickets()` returns list of tickets without queue entries
- `find_mismatched_queue_entries()` returns list of queue entries with mismatched status
- Health check endpoint returns counts of issues found
- Recovery functions log issues but do not auto-fix (manual intervention required)

## Testing
- Unit tests for recovery functions
- Verify health check endpoint returns correct counts
