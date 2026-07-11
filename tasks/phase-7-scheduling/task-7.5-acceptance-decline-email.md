# Task 7.5 — Build Acceptance/Decline Email Agent

## Description
Create the agent that drafts acceptance and decline emails.

## Status
Not Started

## Subtasks
- Create `backend/app/agents/acceptance_email_agent.py`:
  - `draft_acceptance(ticket, blocks) -> DraftEmail`
  - `draft_decline(ticket, reason) -> DraftEmail`
- Use template-based generation (no LLM needed for these)
- Include ticket details in email body

## Dependencies
None

## Acceptance Criteria
- Generates professional acceptance email with schedule
- Generates professional decline email with reason
- Emails include relevant ticket details
- No LLM dependency for these templates
