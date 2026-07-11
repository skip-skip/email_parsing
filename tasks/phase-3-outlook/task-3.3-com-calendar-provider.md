# Task 3.3 — Implement Outlook COM Calendar Provider

## Description
Implement the CalendarProvider interface using pywin32 COM automation.

## Status
Complete

## Subtasks
- Create `backend/app/services/outlook/com_calendar_provider.py`
- Implement `OutlookComCalendarProvider(CalendarProvider)`:
  - `get_events(start, end)`:
    - Access `Namespace.GetDefaultFolder(9)` (olFolderCalendar)
    - Use `Items.Restrict` with date range filter
    - Map COM AppointmentItem to `OutlookCalendarEvent` model
  - `get_free_busy(start, end)`:
    - Use `Namespace.GetFreeBusy` method
    - Parse availability periods
    - Return `FreeBusyInfo` with busy blocks
  - `create_event(title, start, end, body)`:
    - Create `AppointmentItem` via `Items.Add`
    - Set `Subject`, `Start`, `End`, `Body`, `ReminderSet`
    - Save and return `EntryID`
  - `update_event(event_id, fields)`:
    - Get item by EntryID
    - Update specified fields
    - Save
  - `delete_event(event_id)`:
    - Get item by EntryID
    - Delete
- Handle all-day events and recurring appointments

## Dependencies
- Task 3.1

## Acceptance Criteria
- Can read calendar events for a date range
- Can query free/busy information
- Can create, update, and delete calendar events
- Handles timezone correctly
