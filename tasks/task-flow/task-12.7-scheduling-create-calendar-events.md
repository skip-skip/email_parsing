# Task 12.7 — Scheduling Queue: Create Outlook Calendar Events on Approve

## Description
When a schedule is approved, Outlook calendar events should be created for each time block. The `CalendarProvider` and `OutlookComCalendarProvider` implementations exist but are not wired into the scheduling queue. Connect them so approved schedules result in real calendar events.

## Status
Not Started

## Subtasks
- Inject `CalendarProvider` into `SchedulingQueue`:
  - Accept `calendar_provider: CalendarProvider` in constructor or via dependency injection
  - Use `OutlookComCalendarProvider` as the default implementation
- Update `SchedulingQueue.approve_schedule()` (`backend/app/services/queues/scheduling_queue.py`):
  - For each schedule block in `record.suggestion_json["blocks"]`:
    - Call `calendar_provider.create_event(title, start_time, end_time, body)`
    - Store the returned `outlook_event_id` in a new `CalendarEvent` DB record
    - Link the `CalendarEvent` to the ticket via `ticket_id`
  - Set `record.status = "APPROVED"` (already done)
- Update `SchedulingQueue.decline_schedule()`:
  - If the ticket has existing `CalendarEvent` records with Outlook event IDs:
    - Call `calendar_provider.delete_event(outlook_event_id)` for each
    - Remove or mark the `CalendarEvent` records as deleted
- Create `CalendarEventRepository` (`backend/app/services/database/repositories/calendar_event_repository.py`):
  - `create(ticket_id, outlook_event_id, start_time, end_time, duration, status)` — insert a new record
  - `get_by_ticket_id(ticket_id)` — return all events for a ticket
  - `delete_by_ticket_id(ticket_id)` — remove all events for a ticket
- Write unit tests:
  - `approve_schedule()` creates calendar events for each block
  - `approve_schedule()` stores `outlook_event_id` in DB
  - `decline_schedule()` deletes existing calendar events
  - `approve_schedule()` with missing provider logs error gracefully

## Dependencies
- Task 12.6 (approve flow must be updated first)

## Acceptance Criteria
- Approving a schedule creates Outlook calendar events for each time block
- Calendar events are stored in the `calendar_events` table with Outlook event IDs
- Declining a schedule deletes existing calendar events from Outlook
- Calendar events are linked to the ticket
- All existing tests pass
