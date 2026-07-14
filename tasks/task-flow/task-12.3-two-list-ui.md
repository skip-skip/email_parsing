# Task 12.3 — Two-List UI: Pending Review vs. Awaiting Reply

## Description
The missing info queue page currently shows a single list of all items. Split this into two tabs: "Pending Review" (items waiting for user action) and "Awaiting Reply" (emails sent, waiting for client response). This gives visibility into the full lifecycle of missing info requests.

## Status
Not Started

## Subtasks
- Update `MissingInfoQueue.get_queue()` (`backend/app/services/queues/missing_info_queue.py`):
  - Accept an optional `status` parameter (default: `"PENDING"`)
  - Filter by the provided status instead of hardcoded `"PENDING"`
- Update `GET /api/queues/missing-info` endpoint (`backend/app/api/queues.py`):
  - Accept optional `?status=` query parameter
  - Pass status to `queue.get_queue(status=status)`
- Add `listAwaiting` API call in frontend (`frontend/src/services/api.ts`):
  - `api.missingInfo.listAwaiting()` → `GET /api/queues/missing-info?status=AWAITING_REPLY`
- Update `MissingInfoQueue.tsx` (`frontend/src/pages/MissingInfoQueue.tsx`):
  - Add two tabs or segmented control: "Pending Review" and "Awaiting Reply"
  - "Pending Review" tab calls `api.missingInfo.list()` (PENDING items)
  - "Awaiting Reply" tab calls `api.missingInfo.listAwaiting()` (AWAITING_REPLY items)
  - Each tab shows its own count badge
  - Active tab highlights with primary color
- Update `MissingInfoCard.tsx` (`frontend/src/components/MissingInfoCard.tsx`):
  - For AWAITING_REPLY items: show "Sent at {timestamp}" instead of action buttons
  - For AWAITING_REPLY items: disable Edit/Approve/Reject buttons (read-only)
  - Show a "Reply received" indicator if the ticket status has changed from WAITING_FOR_INFORMATION
- Write unit tests:
  - `get_queue(status="PENDING")` returns only pending items
  - `get_queue(status="AWAITING_REPLY")` returns only awaiting-reply items
  - API endpoint accepts `?status=` parameter

## Dependencies
- Task 12.1 (AWAITING_REPLY status must exist)

## Acceptance Criteria
- Missing info queue page shows two tabs: "Pending Review" and "Awaiting Reply"
- Each tab shows the correct items filtered by status
- AWAITING_REPLY items show sent timestamp and are read-only
- Tab counts are accurate
- All existing tests pass
