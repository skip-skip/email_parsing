# Task 4.3 — Build Email Intake Agent

## Description
Create the agent that receives raw emails from the monitor and stores them.

## Status
Not Started

## Subtasks
- Create `backend/app/agents/` directory
- Create `email_intake_agent.py`:
  - Accept `EmailMessage` from monitor
  - Check for duplicates via `email_repository.get_by_entry_id()`
  - If new, create Email record in database
  - Link to existing ticket if `conversation_id` matches
  - Return email_id and whether it's part of an existing thread
- Create `intake_response.py` data model:
  - `email_id: UUID`
  - `is_new_thread: bool`
  - `existing_ticket_id: UUID | None`
  - `ready_for_parsing: bool`
- Wire into monitor callback (called after new email detected)

## Dependencies
- Task 2.2
- Task 2.6
- Task 3.4

## Acceptance Criteria
- New emails are stored in database
- Duplicate emails (same EntryID) are skipped
- Emails with matching conversation_id link to existing ticket
- Returns structured response for downstream processing
