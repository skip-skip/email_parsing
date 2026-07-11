# Task 7.3 — Build Scheduling API Endpoints

## Description
Create FastAPI endpoints for the scheduling queue.

## Status
Not Started

## Subtasks
- Create `backend/app/api/scheduling.py`:
  - `GET /api/queues/scheduling`
  - `GET /api/queues/scheduling/{ticket_id}`
  - `POST /api/queues/scheduling/{ticket_id}/approve`
  - `POST /api/queues/scheduling/{ticket_id}/modify`
  - `POST /api/queues/scheduling/{ticket_id}/decline`
  - `GET /api/scheduling/calendar-availability`

## Dependencies
- Task 7.2

## Acceptance Criteria
- All endpoints return correct data
- Approval creates Outlook events
- Decline sends decline email
- Modification updates blocks
- Calendar availability is returned correctly
