# Task 2.1 — Ticket Model

## Description
Create the Ticket SQLAlchemy model matching the architecture schema.

## Status
Complete

## Subtasks
- Create `backend/app/models/ticket.py`
- Define `Ticket` model with columns:
  - `ticket_id` (UUID primary key, auto-generated)
  - `status` (String, indexed, default `NEW`)
  - `client` (String, nullable)
  - `contact` (String, nullable)
  - `project_number` (String, nullable)
  - `task_description` (Text, nullable)
  - `deadline` (DateTime, nullable)
  - `budget_hours` (Float, nullable)
  - `estimated_hours` (Float, nullable)
  - `priority` (Integer, default 0)
  - `calendar_event_id` (String, nullable)
  - `conversation_id` (String, nullable, indexed)
  - `created_at` (DateTime, server_default=now)
  - `updated_at` (DateTime, onupdate=now)
- Add index on `status` and `conversation_id`
- Add relationship to Email model

## Dependencies
- Task 1.5

## Acceptance Criteria
- Model compiles and maps correctly
- Migration creates table with all columns and indexes
