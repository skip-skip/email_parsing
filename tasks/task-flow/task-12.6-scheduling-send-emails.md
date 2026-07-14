# Task 12.6 — Scheduling Queue: Send Accept/Decline Emails

## Description
The scheduling queue's approve and decline actions currently only flip DB status flags — no emails are actually sent. The frontend modals promise "send an acceptance email" and "send a decline email" but these are not implemented. Fix this so approve sends a confirmation email and decline sends a decline-explanation email, both via Outlook reply-all.

## Status
Not Started

## Subtasks
- Update `SchedulingQueue.approve_schedule()` (`backend/app/services/queues/scheduling_queue.py`):
  - Look up the ticket's `conversation_id` from the `tickets` table
  - Compose acceptance email body: "Your schedule has been accepted. Calendar events have been created for [dates/times]."
  - Call `EmailProvider.send_reply_all(conversation_id, body)` to send the email
  - Set `record.status = "APPROVED"` (already done)
- Update `SchedulingQueue.decline_schedule()` (`backend/app/services/queues/scheduling_queue.py`):
  - Look up the ticket's `conversation_id` from the `tickets` table
  - Accept a `reason: str` parameter from the frontend (user-entered free text, e.g. "This won't work with my schedule")
  - Compose decline email body: "Unfortunately, we are unable to proceed with this task at this time. Reason: {reason}"
  - Call `EmailProvider.send_reply_all(conversation_id, body)` to send the email
  - Set `record.status = "DECLINED"` (already done)
  - Persist the rejection reason to the DB
- Add `rejection_reason: Mapped[str | None]` column to `SchedulingQueueRecord` (`backend/app/models/scheduling_queue_record.py`)
- Create Alembic migration for the new column
- Update `backend/app/api/scheduling.py` decline endpoint to accept `reason` in request body
- Write unit tests:
  - `approve_schedule()` sends email via `send_reply_all()`
  - `decline_schedule()` sends email with reason via `send_reply_all()`
  - `approve_schedule()` with missing ticket logs error gracefully
  - `decline_schedule()` persists rejection reason

## Dependencies
None

## Acceptance Criteria
- Approving a schedule sends a confirmation email via Outlook reply-all
- Declining a schedule sends a decline email with user-entered reason via Outlook reply-all
- Rejection reasons are persisted in the database
- All existing tests pass
