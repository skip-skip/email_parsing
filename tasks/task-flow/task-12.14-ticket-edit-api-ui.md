# Task 12.14 — Ticket Edit API + UI

## Description
There is no way to edit a ticket's fields through the API or UI. If the AI extracted wrong information (wrong client name, wrong deadline, missing project number), the user has no way to fix it without modifying the database directly. Add a PATCH endpoint and an edit UI.

## Status
Not Started

## Subtasks
- Add `PATCH /api/tickets/{ticket_id}` endpoint (`backend/app/api/tickets.py`):
  - Accept a JSON body with editable fields: `client`, `contact`, `project_number`, `task_description`, `deadline`, `budget_hours`, `estimated_hours`, `priority`, `notes`
  - Validate each field:
    - `deadline`: must be a valid datetime, must be in the future (or null to clear)
    - `priority`: must be a valid `Priority` enum value
    - `budget_hours` / `estimated_hours`: must be positive numbers (or null)
    - `client` / `contact`: must be non-empty strings (or null)
  - Update the ticket in the database via `TicketRepository.update()`
  - Return the updated ticket
  - Log the edit to `ai_logs` with action="manual_edit"
- Add `api.tickets.update(ticketId, fields)` method (`frontend/src/services/api.ts`)
- Add Edit button to `TaskDetail.tsx` (`frontend/src/pages/TaskDetail.tsx`):
  - Show "Edit" button in the page header
  - Clicking opens an edit modal or switches the page to edit mode
  - Editable fields: client, contact, project_number, task_description, deadline, budget_hours, estimated_hours, priority
  - Show validation errors inline
  - On save, call `api.tickets.update()` and refresh the page
  - Show success toast after save
- Write unit tests:
  - `PATCH /api/tickets/{id}` updates allowed fields
  - `PATCH /api/tickets/{id}` rejects invalid deadline (past date)
  - `PATCH /api/tickets/{id}` rejects invalid priority
  - `PATCH /api/tickets/{id}` with empty body returns unchanged ticket
  - `PATCH /api/tickets/{id}` logs edit to ai_logs

## Dependencies
None

## Acceptance Criteria
- `PATCH /api/tickets/{id}` updates ticket fields in the database
- Invalid field values return clear error messages
- TaskDetail page has an Edit button that opens an edit form
- Edits are saved and reflected immediately
- Edits are logged to the AI audit trail
- All existing tests pass
