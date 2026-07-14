# Task 12.10 — Close Task: Completion Notification Email Draft

## Description
When a task is closed, a completion notification email should be drafted and sent to the client. This requires a new prompt for generating completion summaries, integration with the email draft agent, and sending the email via Outlook.

## Status
Not Started

## Subtasks
- Create completion notification prompt (`backend/app/prompts/completion_notification.py`):
  - System prompt: "You are drafting a task completion notification email. Summarize what was done and thank the client."
  - User prompt template: includes task description, deadline, any calendar events, and notes
  - Version string for AI logging
- Add `draft_completion_notification()` method to `EmailDraftAgent` (`backend/app/agents/email_draft_agent.py`):
  - Accept ticket context (task_description, deadline, calendar_events, sender)
  - Use the completion notification prompt with the LLM
  - Fall back to a template-based draft if LLM fails
  - Return a `DraftEmail` with the completion notification
- Update `POST /api/tickets/{ticket_id}/complete` endpoint (`backend/app/api/tickets.py`):
  - After transitioning to COMPLETED, call `EmailDraftAgent.draft_completion_notification()`
  - Send the email via `EmailProvider.send_reply_all(conversation_id, body)`
  - Store the email in the `ai_logs` table for audit
- Write unit tests:
  - Completion notification draft includes task summary
  - Fallback template works when LLM fails
  - Email is sent via `send_reply_all()`
  - Email is logged to `ai_logs`

## Dependencies
- Task 12.9 (complete endpoint must exist)

## Acceptance Criteria
- Closing a task generates a completion notification email via LLM
- The email is sent to the client via Outlook reply-all
- The email is logged to the AI audit trail
- Fallback template works when LLM is unavailable
- All existing tests pass
