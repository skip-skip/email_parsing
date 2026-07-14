# Task 12.5 — Awaiting-Reply Card State in Frontend

## Description
Polish the missing info queue cards to properly reflect the awaiting-reply lifecycle. When a reply is received for a ticket in AWAITING_REPLY status, the card should indicate this and provide a link to view the updated ticket.

## Status
Not Started

## Subtasks
- Update `MissingInfoCard.tsx` (`frontend/src/components/MissingInfoCard.tsx`):
  - For AWAITING_REPLY items:
    - Show "Sent at {formatted timestamp}" below the ticket header
    - Show a pulsing green dot or "Awaiting reply" badge
    - Disable all action buttons (Edit Draft, Approve, Reject)
    - Show "View Ticket" button that navigates to `/active-tasks/{ticketId}`
  - For PENDING items:
    - Keep existing behavior (Edit Draft, Approve, Reject buttons)
- Add visual distinction between PENDING and AWAITING_REPLY cards:
  - PENDING: default card style (current)
  - AWAITING_REPLY: subtle left border color (e.g., blue or green) to indicate "in progress"
- Add a "Last reply" section if the ticket has been replied to:
  - Show the date of the last email in the conversation
  - Show a brief summary if available from the ticket's `task_description`
- Write component tests:
  - AWAITING_REPLY card shows sent timestamp
  - AWAITING_REPLY card disables action buttons
  - AWAITING_REPLY card shows "View Ticket" link
  - PENDING card shows action buttons

## Dependencies
- Task 12.1 (AWAITING_REPLY status)
- Task 12.3 (two-list UI)

## Acceptance Criteria
- AWAITING_REPLY cards show sent timestamp and are read-only
- AWAITING_REPLY cards have a visual distinction from PENDING cards
- "View Ticket" link navigates to the ticket detail page
- PENDING cards retain existing behavior
- All existing tests pass
