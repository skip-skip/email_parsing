# Task 8.2 — Enhanced AI Logging

## Description
Build comprehensive logging for all AI interactions.

## Status
Complete

## Subtasks
- Enhance `AILog` model with additional fields:
  - `input_tokens: Integer`
  - `output_tokens: Integer`
  - `success: Boolean`
  - `error_message: Text` (nullable)
- Create `backend/app/services/llm/ai_logger.py`:
  - `log_interaction(...) -> AILog`
  - Automatically calculate execution time
  - Store raw prompt and response for debugging
- Create `backend/app/api/ai_logs.py`:
  - `GET /api/ai-logs` — list all logs with pagination
  - `GET /api/ai-logs/{ticket_id}` — logs for specific ticket
  - `GET /api/ai-logs/stats` — aggregated statistics
- Add filtering by model, prompt_version, success, date range

## Dependencies
- Task 2.4
- Task 2.6

## Acceptance Criteria
- All AI interactions are logged with full context
- Logs are queryable via API
- Statistics are computed correctly
- Raw prompts/responses available for debugging
