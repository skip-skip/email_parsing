# Task 3.4 — Implement APScheduler Outlook Monitor

## Description
Build the background polling service that detects new emails.

## Status
Complete

## Subtasks
- Create `backend/app/services/outlook/monitor.py`
- Implement `OutlookMonitor` class:
  - Initialize APScheduler `BackgroundScheduler`
  - Add job that runs every N seconds (configurable via `POLL_INTERVAL_SECONDS`, default 30)
  - On each tick:
    1. Call `email_provider.get_new_messages()`
    2. For each new message, check if `entry_id` already exists in DB
    3. If new, store in Email table and trigger workflow
    4. Log detection count
  - Track last poll time to avoid duplicate processing
  - Graceful shutdown: stop scheduler on app shutdown
- Add startup/shutdown hooks to FastAPI app:
  - `@app.on_event("startup")` → `monitor.start()`
  - `@app.on_event("shutdown")` → `monitor.stop()`
- Add configuration:
  - `POLL_INTERVAL_SECONDS` (default 30)
  - `OUTLOOK_ENABLED` (default true, for testing without Outlook)

## Dependencies
- Task 3.2
- Task 1.5
- Task 1.6

## Acceptance Criteria
- Monitor starts on app startup
- Polls at configured interval
- New emails are detected and stored
- Duplicate emails are skipped
- Monitor stops cleanly on app shutdown
- Can disable monitor for testing
