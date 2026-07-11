# Task 1.6 — Set Up Logging

## Description
Configure structured logging across the application.

## Status
Not Started

## Subtasks
- Install Loguru (or configure Python logging)
- Create `backend/app/services/logging.py` with:
  - Console handler with colored output
  - File handler with rotation
  - JSON formatter for production
- Configure log levels via environment variable
- Add request ID middleware to FastAPI
- Ensure all loggers propagate through middleware

## Dependencies
- Task 1.1

## Acceptance Criteria
- Logs output to console and file
- Request IDs appear in log entries
- Log level configurable via env var
