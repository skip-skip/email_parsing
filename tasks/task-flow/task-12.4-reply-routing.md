# Task 12.4 — Reply Routing: Wire ConversationHandler into EmailProcessor

## Description
When a reply arrives for a ticket in `WAITING_FOR_INFORMATION` status, the system currently creates a duplicate ticket instead of merging the reply into the existing one. The `ConversationHandler.handle_reply()` method exists and is fully implemented but is never called from production code. Wire it into the email processing pipeline so replies are detected, routed, and merged correctly.

## Status
Not Started

## Subtasks
- Fix state transition map (`backend/app/workflows/transitions.py`):
  - Add `WAITING_FOR_INFORMATION -> READY_FOR_SCHEDULING` to `VALID_TRANSITIONS`
  - This is needed because `ConversationHandler.handle_reply()` transitions to `READY_FOR_SCHEDULING` when all fields are complete
- Update `EmailProcessor.process_new_email()` (`backend/app/services/email_processor.py`):
  - Before classifying a new email, check if `message.conversation_id` matches an existing ticket via `TicketRepository.get_by_conversation_id()`
  - If a ticket exists and its status is `WAITING_FOR_INFORMATION`:
    - Route to `ConversationHandler.handle_reply(conversation_id, message)` instead of creating a new ticket
    - If `handle_reply()` succeeds and ticket transitions to `READY_FOR_SCHEDULING`:
      - Remove the ticket from the missing info queue (set status to `"REPLIED"`)
      - Log the transition
    - If `handle_reply()` finds fields are still missing:
      - Re-queue with updated draft (call `_create_missing_info_entry()` with updated fields)
    - Return `ProcessingResult` with the existing `ticket_id`
  - If no matching ticket exists or ticket is not in `WAITING_FOR_INFORMATION`:
    - Proceed with the current new-ticket pipeline (classify → create → workflow)
- Add `remove_from_queue(ticket_id)` method to `MissingInfoQueue` (`backend/app/services/queues/missing_info_queue.py`):
  - Set `record.status = "REMOVED"` (or `"REPLIED"`) to remove from both lists
- Write unit tests:
  - Reply to WAITING_FOR_INFORMATION ticket → routes to ConversationHandler
  - Reply merges fields and transitions to READY_FOR_SCHEDULING
  - Reply with still-missing fields → re-queues with updated draft
  - Reply to non-WAITING_FOR_INFORMATION ticket → creates new ticket (normal flow)
  - Reply with unknown conversation_id → creates new ticket (normal flow)

## Dependencies
- Task 12.1 (AWAITING_REPLY status and queue entry must exist)

## Acceptance Criteria
- Replies to WAITING_FOR_INFORMATION tickets are routed to ConversationHandler
- Reply fields are merged into the existing ticket
- If all missing fields are provided, ticket transitions to READY_FOR_SCHEDULING
- If fields are still missing, ticket is re-queued with updated draft
- No duplicate tickets are created for replies
- The state transition WAITING_FOR_INFORMATION → READY_FOR_SCHEDULING is valid
- All existing tests pass
