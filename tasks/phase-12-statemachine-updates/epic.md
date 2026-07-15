# Epic 12 -- State Machine Updates

## Goal
Fix the 5 known integration issues from `docs/state_flow.txt` section 7. Align the transition map with actual code paths, add DENIED status, fix UI visibility gaps, and add recovery for ticket/queue drift.

## Status
Not Started

## Tasks
| Task | Title | Status | Dependencies |
|------|-------|--------|-------------|
| 12.1 | Add DENIED Status to TicketStatus Enum | Not Started | None |
| 12.2 | Remove PENDING_USER_APPROVAL from Transition Map | Not Started | None |
| 12.3 | Add EXTRACTION_FAILED to ACTIVE_STATUSES | Not Started | None |
| 12.4 | Add DENIED to CLOSED_STATUSES + Clean Up Phantom Statuses | Not Started | 12.1 |
| 12.5 | Wire DENIED into Scheduling Queue Decline Path | Not Started | 12.1 |
| 12.6 | Add Recovery Mechanism for Ticket/Queue Status Drift | Not Started | None |
| 12.7 | Improve _persist_ticket_status Error Handling | Not Started | None |
| 12.8 | Update state_flow.txt to Reflect All Changes | Not Started | 12.1-12.7 |
| 12.9 | Run Tests and Verify Changes | Not Started | 12.1-12.8 |

## Gaps Between Current and Planned Pipeline

### Gap 1: EXTRACTION_FAILED invisible in UI
- **Current**: `ACTIVE_STATUSES` at `tickets.py:21` does not include EXTRACTION_FAILED
- **Planned**: Add EXTRACTION_FAILED to ACTIVE_STATUSES
- **Files**: `backend/app/api/tickets.py:21`

### Gap 2: PENDING_USER_APPROVAL unreachable
- **Current**: In `VALID_TRANSITIONS` at `transitions.py:19-20` but no code path reaches it
- **Planned**: Remove from transition map
- **Files**: `backend/app/workflows/transitions.py:19-20`

### Gap 3: No DENIED status for schedule decline
- **Current**: `scheduling_queue.py:215` transitions to WAITING_FOR_INFORMATION on decline
- **Planned**: Add DENIED as terminal state, wire into decline path
- **Files**: `backend/app/workflows/states.py`, `backend/app/workflows/transitions.py`, `backend/app/services/queues/scheduling_queue.py:215`

### Gap 4: CLOSED_STATUSES has phantom statuses
- **Current**: `tickets.py:167` lists "DECLINED" and "CANCELLED" but neither exists in TicketStatus enum
- **Planned**: Replace with DENIED, remove phantom strings
- **Files**: `backend/app/api/tickets.py:167`

### Gap 5: No archive endpoint
- **Current**: `VALID_TRANSITIONS` allows COMPLETED -> ARCHIVED but no API endpoint exists
- **Planned**: Not addressed in this phase (out of scope)
- **Files**: None

### Gap 6: Ticket/queue status drift
- **Current**: Queue creation can fail silently, leaving ticket without queue entry
- **Planned**: Add recovery mechanism
- **Files**: New file `backend/app/services/recovery.py`

### Gap 7: Silent exception swallowing
- **Current**: `_persist_ticket_status` at `email_processor.py:346-349` catches all exceptions
- **Planned**: Add logging and consider re-raise
- **Files**: `backend/app/services/email_processor.py:346-349`

## Acceptance Criteria
- DENIED status exists in TicketStatus enum
- PENDING_USER_APPROVAL removed from VALID_TRANSITIONS
- EXTRACTION_FAILED appears in Active Tasks view
- DENIED appears in Closed Tasks view
- Scheduling queue decline transitions ticket to DENIED instead of WAITING_FOR_INFORMATION
- Recovery mechanism detects and reports orphaned tickets
- _persist_ticket_status logs failures at ERROR level
- All existing tests pass
- state_flow.txt reflects all changes
