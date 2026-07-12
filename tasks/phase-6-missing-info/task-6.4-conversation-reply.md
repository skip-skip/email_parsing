# Task 6.4 — Conversation Reply Handling

## Description
Handle incoming replies to missing information requests.

## Status
Complete

## Subtasks
- Create `backend/app/services/conversation_handler.py`:
  - When monitor detects a reply to a ticket in WAITING_FOR_INFORMATION:
    1. Find existing ticket by conversation_id
    2. Re-parse the reply email
    3. Merge new information into ticket (via ConversationTracker)
    4. Re-validate ticket
    5. If now complete → move to READY_FOR_SCHEDULING
    6. If still incomplete → update missing fields and draft new request
  - Handle multiple replies
  - Handle edge cases (partial info, no info, new work request)

## Dependencies
- Task 4.5
- Task 5.4
- Task 6.2

## Acceptance Criteria
- Replies are associated with existing tickets
- New information merges correctly
- Ticket progresses when all fields are complete
- Partial information updates the missing fields list
- Multiple replies are handled correctly
