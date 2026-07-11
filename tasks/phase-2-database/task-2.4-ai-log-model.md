# Task 2.4 — AILog Model

## Description
Create the AILog model for tracking all LLM interactions.

## Status
Complete

## Subtasks
- Create `backend/app/models/ai_log.py`
- Define `AILog` model with columns:
  - `log_id` (UUID primary key, auto-generated)
  - `ticket_id` (UUID, foreign key to tickets, nullable)
  - `model` (String)
  - `prompt_version` (String)
  - `prompt` (Text)
  - `response` (Text)
  - `parsed_json` (JSON, nullable)
  - `confidence` (Float, nullable)
  - `execution_time_ms` (Integer, nullable)
  - `created_at` (DateTime, server_default=now)
- Add index on `ticket_id` and `created_at`

## Dependencies
- Task 1.5

## Acceptance Criteria
- Model compiles and maps correctly
- Migration creates table
