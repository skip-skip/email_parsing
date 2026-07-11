# Task 2.2 — Email Model

## Description
Create the Email SQLAlchemy model.

## Status
Complete

## Subtasks
- Create `backend/app/models/email.py`
- Define `Email` model with columns:
  - `email_id` (UUID primary key, auto-generated)
  - `conversation_id` (String, indexed)
  - `entry_id` (String, unique — Outlook EntryID)
  - `sender` (String)
  - `subject` (String)
  - `body` (Text)
  - `received_time` (DateTime)
  - `attachments` (JSON, default empty list)
  - `created_at` (DateTime, server_default=now)
- Add foreign key to Ticket (nullable — assigned after parsing)
- Add relationship back to Ticket

## Dependencies
- Task 1.5

## Acceptance Criteria
- Model compiles and maps correctly
- Migration creates table
- EntryID uniqueness enforced at DB level
