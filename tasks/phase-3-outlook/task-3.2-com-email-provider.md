# Task 3.2 — Implement Outlook COM Email Provider

## Description
Implement the EmailProvider interface using pywin32 COM automation.

## Status
Not Started

## Subtasks
- Create `backend/app/services/outlook/com_email_provider.py`
- Implement `OutlookComEmailProvider(EmailProvider)`:
  - Connect to Outlook instance via `win32com.client.Dispatch("Outlook.Application")`
  - `get_new_messages()`:
    - Access `Namespace.GetDefaultFolder(6)` (olFolderInbox)
    - Filter for unread messages (`UnRead == True`)
    - Map COM message objects to `EmailMessage` models
    - Extract `EntryID`, `ConversationID`, `SenderName`, `Subject`, `Body`, `ReceivedTime`
    - Handle attachments (save to temp dir, store paths)
  - `get_conversation(conversation_id)`:
    - Use `Items.Restrict` with `"[ConversationID] = '...'"` filter
    - Return all messages in thread, sorted by received time
  - `send_reply(conversation_id, body)`:
    - Get original message by EntryID
    - Use `message.Reply()` or `message.ReplyAll()`
    - Set body and send
  - Handle COM errors gracefully (Outlook not running, permission denied)
- Add connection retry logic (3 attempts with backoff)

## Dependencies
- Task 3.1

## Acceptance Criteria
- Can connect to running Outlook instance
- Can list unread inbox messages
- Can retrieve conversation threads
- Can send a reply to a specific thread
- COM errors are caught and logged
