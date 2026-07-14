# Task 12.11 — Closed Tasks Page: Frontend

## Description
Add a "Closed Tasks" page to the frontend so users can view completed and archived tasks. This includes a new route, page component, sidebar navigation link, and the ability to close tasks from the Active Tasks page.

## Status
Not Started

## Subtasks
- Add "Close Task" button to `TaskDetail.tsx` (`frontend/src/pages/TaskDetail.tsx`):
  - Show a "Close Task" button in the page header or action area
  - Button triggers a confirmation modal: "This will mark the task as complete and send a completion notification to the client."
  - On confirm, call `api.tickets.complete(ticketId)` and navigate to `/closed-tasks`
  - Only show the button if the ticket status is closable (`IN_PROGRESS`, `CALENDAR_CREATED`, `ACCEPTED`)
- Create `ClosedTasks.tsx` page (`frontend/src/pages/ClosedTasks.tsx`):
  - Similar layout to `ActiveTasks.tsx`
  - Calls `api.tickets.listClosed()` to fetch completed/archived tickets
  - Shows status badges: COMPLETED (green checkmark), ARCHIVED (gray)
  - Supports filtering by client and sorting by deadline/created/priority
  - Shows a "View Ticket" link for each item
  - Auto-refresh every 30 seconds
- Add `ClosedTasks` route to `App.tsx` (`frontend/src/App.tsx`):
  - Route: `/closed-tasks`
- Add "Closed Tasks" to sidebar navigation:
  - Find the sidebar/nav component and add a link with a check-circle or archive icon
- Add badge colors for COMPLETED and ARCHIVED in `TaskRow.tsx`:
  - COMPLETED: green badge with checkmark icon
  - ARCHIVED: gray badge with archive icon
- Write component tests:
  - "Close Task" button appears for closable tickets
  - "Close Task" button does not appear for non-closable tickets
  - Closed Tasks page renders completed tickets
  - Status badges render correctly

## Dependencies
- Task 12.9 (API endpoints must exist)
- Task 12.10 (completion notification must be sent)

## Acceptance Criteria
- "Close Task" button appears on TaskDetail for closable tickets
- Clicking "Close Task" confirms, sends completion email, and navigates to Closed Tasks
- Closed Tasks page shows completed and archived tickets
- Sidebar has a "Closed Tasks" navigation link
- Status badges render correctly for COMPLETED and ARCHIVED
- All existing tests pass
