# Task 6.3 — Build Missing Info API Endpoints

## Description
Create FastAPI endpoints for the missing information queue.

## Status
Complete

## Subtasks
- Create `backend/app/api/queues.py`:
  - `GET /api/queues/missing-info`
  - `GET /api/queues/missing-info/{ticket_id}`
  - `POST /api/queues/missing-info/{ticket_id}/approve`
  - `POST /api/queues/missing-info/{ticket_id}/reject`
  - `PUT /api/queues/missing-info/{ticket_id}/draft`
- Add request/response Pydantic models
- Add error handling (404 for missing ticket, 409 for already processed)

## Dependencies
- Task 6.2

## Acceptance Criteria
- All endpoints return correct data
- Approval sends email via Outlook
- Rejection removes from queue
- Draft updates persist
- Proper HTTP status codes
