# Task 12.17 — ConversationHandler: Persist Merged Fields to Database

## Description
The `ConversationHandler.handle_reply()` merges reply fields into a local dict and re-validates, but never writes the updated field values back to the database. This means reply data is lost on restart. Fix this so merged fields are persisted and the ticket status is updated accordingly.

## Status
Not Started

## Subtasks
- Update `ConversationHandler.handle_reply()` (`backend/app/services/conversation_handler.py`):
  - After merging fields and re-validating, call `ticket_repo.update(ticket_id, merged_fields)` to persist changes
  - Use `TicketRepository.update()` to write the merged field values to the database
  - If validation passes (all required fields present), transition ticket to `READY_FOR_SCHEDULING`
  - If validation still fails (fields still missing), re-queue the ticket with updated draft
  - Log the merge operation to `ai_logs` with action="reply_merge"
- Update `ConversationHandler._merge_fields()` to also handle:
  - Updating `contact` if the reply provides a new contact name
  - Updating `project_number` if the reply provides a project number
  - Updating `task_description` if the reply adds more context
- Write unit tests:
  - `handle_reply()` persists merged fields to database
  - `handle_reply()` transitions to READY_FOR_SCHEDULING when all fields present
  - `handle_reply()` re-queues when fields still missing
  - `handle_reply()` logs merge operation to ai_logs
  - `handle_reply()` handles null/missing fields gracefully

## Dependencies
- Task 12.16 (state machine enforcement should be in place)

## Acceptance Criteria
- Reply fields are persisted to the database after merge
- Ticket status transitions correctly based on re-validation
- Re-queued tickets have updated drafts
- Merge operations are logged to the audit trail
- All existing tests pass
