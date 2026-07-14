# Task 12.13 — Pagination for Active Tasks

## Description
The Active Tasks page ignores the `offset`/`limit` params from the `PaginatedResponse` — it fetches the first page with no way to load more. Users with more than 50 tasks will see a truncated list. Add proper pagination controls.

## Status
Not Started

## Subtasks
- Update `ActiveTasks.tsx` (`frontend/src/pages/ActiveTasks.tsx`):
  - Track `currentPage` and `pageSize` state (default: page=1, pageSize=50)
  - Pass `offset` and `limit` to `api.tickets.listActive()` based on current page
  - Calculate total pages from `response.total` and `pageSize`
  - Add pagination controls at the bottom of the list:
    - Previous/Next buttons
    - Page number display ("Page 1 of 3")
    - Page size selector (25, 50, 100)
  - Reset to page 1 when filters change
- Add `api.tickets.listActive()` param support if missing:
  - Ensure `offset` and `limit` params are passed through to the backend
  - Backend already supports these params via `TicketRepository.get_active_tickets()`
- Write tests:
  - Pagination renders with correct page count
  - Previous/Next buttons navigate pages
  - Page size change resets to page 1
  - Filter change resets to page 1

## Dependencies
None

## Acceptance Criteria
- Active Tasks page shows pagination controls when total > pageSize
- Previous/Next buttons work correctly
- Page size can be changed (25, 50, 100)
- Filters reset pagination to page 1
- All existing tests pass
