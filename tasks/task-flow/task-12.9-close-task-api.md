# Task 12.9 — Close Task: API Endpoint & State Transition

## Description
Add the ability to close/complete a task from the Active Tasks page. This requires a new API endpoint that transitions the ticket to COMPLETED status and triggers the closure flow (email draft generation, move to closed list).

## Status
Not Started

## Subtasks
- Add `POST /api/tickets/{ticket_id}/complete` endpoint (`backend/app/api/tickets.py`):
  - Look up the ticket by ID
  - Validate the ticket is in a closable status (`IN_PROGRESS`, `CALENDAR_CREATED`, `ACCEPTED`)
  - Call `transition_ticket(ticket_id, TicketStatus.COMPLETED)` to transition the ticket
  - Return the updated ticket
- Add `GET /api/tickets/closed` endpoint (`backend/app/api/tickets.py`):
  - Query tickets with status `COMPLETED` or `ARCHIVED`
  - Support the same filtering/sorting as `list_active_tickets`
  - Return paginated response
- Add `COMPLETED_STATUSES` constant: `("COMPLETED", "ARCHIVED")`
- Add frontend API methods (`frontend/src/services/api.ts`):
  - `api.tickets.complete(ticketId)` → `POST /api/tickets/{ticket_id}/complete`
  - `api.tickets.listClosed()` → `GET /api/tickets/closed`
- Write unit tests:
  - `POST /api/tickets/{id}/complete` transitions ticket to COMPLETED
  - `POST /api/tickets/{id}/complete` with invalid status returns error
  - `GET /api/tickets/closed` returns completed/archived tickets

## Dependencies
None

## Acceptance Criteria
- `POST /api/tickets/{ticket_id}/complete` transitions the ticket to COMPLETED
- `GET /api/tickets/closed` returns completed and archived tickets
- Tickets in COMPLETED status are not shown on Active Tasks page
- All existing tests pass
