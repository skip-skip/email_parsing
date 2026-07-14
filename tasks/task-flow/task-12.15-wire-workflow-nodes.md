# Task 12.15 — Wire Workflow Nodes to Real Logic

## Description
Several workflow nodes are stubs that return hardcoded values instead of performing real work. The `plan_schedule` node doesn't add items to the SchedulingQueue, `create_calendar_event` returns a fake `evt-{id}` string, and `draft_missing_info_email` uses a hardcoded template instead of the LLM-powered `EmailDraftAgent`. Wire these nodes to real implementations.

## Status
Not Started

## Subtasks
- Fix `plan_schedule` node (`backend/app/workflows/nodes/plan_schedule.py`):
  - Use `CalendarPlanningAgent` (or inline logic) to generate a schedule suggestion
  - Create a `SchedulingQueueRecord` with status="PENDING" and the suggestion JSON
  - Link the record to the ticket via `ticket_id`
  - Return the queue record ID in the workflow state
- Fix `create_calendar_event` node (`backend/app/workflows/nodes/create_calendar_event.py`):
  - Use `OutlookComCalendarProvider.create_event()` to create a real Outlook calendar event
  - Store the `outlook_event_id` in a `CalendarEvent` DB record
  - Link the `CalendarEvent` to the ticket
  - Return the event ID in the workflow state
  - If calendar provider is unavailable (e.g., no Outlook), log a warning and skip
- Fix `draft_missing_info_email` node (`backend/app/workflows/nodes/draft_missing_info_email.py`):
  - Use `EmailDraftAgent.draft()` to generate an LLM-powered email draft
  - Fall back to the current hardcoded template if LLM fails
  - The generated draft should already be written to `missing_info_queue` (fixed in Phase X)
- Fix `dispatch_task` node (`backend/app/workflows/nodes/dispatch_task.py`):
  - If the workflow reached this node with all fields valid, transition ticket to `READY_FOR_SCHEDULING`
  - If fields are still missing, transition to `WAITING_FOR_INFORMATION`
  - Return the final status
- Write unit tests for each node:
  - `plan_schedule` creates a SchedulingQueueRecord
  - `create_calendar_event` creates a CalendarEvent with real Outlook event ID
  - `draft_missing_info_email` uses EmailDraftAgent and falls back to template
  - `dispatch_task` transitions ticket to correct status

## Dependencies
- Task 12.16 (state machine enforcement should be in place first)
- Task 12.7 (CalendarEvent model and repository should exist)

## Acceptance Criteria
- `plan_schedule` creates real SchedulingQueue records that appear in the scheduling queue UI
- `create_calendar_event` creates real Outlook calendar events
- `draft_missing_info_email` generates LLM-powered drafts with template fallback
- `dispatch_task` correctly transitions ticket status
- All workflow nodes perform real work, not stubs
- All existing tests pass
