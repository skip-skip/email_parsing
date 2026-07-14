# Task 12.19 — Ticket Detail Links from Queue Items

## Description
MissingInfoCard and ScheduleCard display truncated ticket IDs but don't link to the ticket detail page. Users can't inspect the full ticket context (description, deadline, calendar events) from the queue. Add clickable links that navigate to the ticket detail view.

## Status
Not Started

## Subtasks
- Update `MissingInfoCard.tsx` (`frontend/src/components/MissingInfoCard.tsx`):
  - Make the ticket ID clickable — navigates to `/active-tasks/{ticket_id}`
  - Open in the same tab (not new tab) for consistent navigation
  - Style as a link (underline on hover, blue text)
- Update `ScheduleCard.tsx` (`frontend/src/components/ScheduleCard.tsx`):
  - Same as MissingInfoCard — make ticket ID clickable
  - Navigate to `/active-tasks/{ticket_id}`
- Update `TaskDetail.tsx` (`frontend/src/pages/TaskDetail.tsx`):
  - Add an "AI Logs" section that calls `api.aiLogs.getByTicket(ticketId)`
  - Show the last 5 log entries for this ticket (timestamp, action, model, success/fail)
  - Add "View All Logs" link that navigates to `/ai-logs` with ticket filter
- Write tests:
  - MissingInfoCard ticket ID links to correct route
  - ScheduleCard ticket ID links to correct route
  - TaskDetail shows AI logs for the ticket
  - TaskDetail "View All Logs" navigates correctly

## Dependencies
None

## Acceptance Criteria
- MissingInfoCard ticket ID is a clickable link to ticket detail
- ScheduleCard ticket ID is a clickable link to ticket detail
- TaskDetail shows recent AI logs for the ticket
- All existing tests pass
