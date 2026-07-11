# Task 6.2 — Build Missing Information Queue Service

## Description
Create the service that manages the missing information review queue.

## Status
Not Started

## Subtasks
- Create `backend/app/services/queues/` directory
- Create `missing_info_queue.py`:
  - `add_to_queue(ticket_id, draft) -> QueueItem`
  - `get_queue() -> list[QueueItem]`
  - `approve_item(ticket_id, edits=None) -> None`
  - `reject_item(ticket_id, reason=None) -> None`
  - `update_draft(ticket_id, new_draft) -> None`
- Create `queue_item.py` model:
  - `ticket_id: UUID`
  - `ticket: Ticket`
  - `draft_email: DraftEmail`
  - `missing_fields: list[str]`
  - `created_at: DateTime`
  - `status: str` (PENDING, APPROVED, REJECTED)

## Dependencies
- Task 5.1
- Task 6.1
- Task 2.6

## Acceptance Criteria
- Tickets are added to queue with draft
- Queue returns all pending items with full context
- Approval sends email and updates status
- Rejection is recorded
- Drafts can be edited before approval
