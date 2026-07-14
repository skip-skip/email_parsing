# Task 12.1 — Send Email on Approve + Reply-All + AWAITING_REPLY Status

## Description
The "Approve & Send" action in the missing info queue currently only flips a DB status flag — no email is actually sent. Fix this so clicking approve sends a reply-all email via Outlook and moves the ticket to AWAITING_REPLY status. Add a `sent_at` timestamp to track when the email was sent.

## Status
Not Started

## Subtasks
- Add `send_reply_all(conversation_id, body)` abstract method to `EmailProvider` base class (`backend/app/services/outlook/base.py`)
- Implement `send_reply_all()` in `OutlookComEmailProvider` (`backend/app/services/outlook/com_email_provider.py`):
  - Use Outlook's `message.ReplyAll()` instead of `message.Reply()`
  - Same pattern as `_send_reply()`: filter by ConversationID, sort descending, pick newest, call `.ReplyAll()`, set body, `.Send()`
  - Run in `asyncio.to_thread()` like existing `send_reply()`
- Add `sent_at: Mapped[datetime | None]` column to `MissingInfoQueueRecord` (`backend/app/models/missing_info_queue_record.py`)
- Create Alembic migration for the `sent_at` column
- Update `MissingInfoQueue.approve_item()` (`backend/app/services/queues/missing_info_queue.py`):
  - Look up the ticket's `conversation_id` from the `tickets` table
  - Call `EmailProvider.send_reply_all(conversation_id, draft.body)` to send the email
  - Set `record.status = "AWAITING_REPLY"` (not "APPROVED")
  - Set `record.sent_at = datetime.now()`
  - Return the updated queue item
- Update `GET /api/queues/missing-info` to only return `PENDING` items (already does this)
- Write unit tests:
  - `approve_item()` sends email via `send_reply_all()`
  - `approve_item()` sets status to `AWAITING_REPLY`
  - `approve_item()` sets `sent_at` timestamp
  - `approve_item()` with missing ticket raises/logs error
  - `get_queue()` returns only PENDING items (not AWAITING_REPLY)

## Dependencies
None

## Acceptance Criteria
- Clicking "Approve & Send" sends a reply-all email via Outlook
- Queue item status changes to AWAITING_REPLY after approval
- `sent_at` timestamp is recorded
- `get_queue()` only returns PENDING items (approved items are filtered out)
- All existing tests pass
