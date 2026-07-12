# Task 6.1 — Build Email Draft Agent

## Description
Create the agent that drafts emails requesting missing information from clients.

## Status
Complete

## Subtasks
- Create `backend/app/agents/email_draft_agent.py`:
  - Accept ticket data and list of missing fields
  - Call `missing_info_draft` prompt via Ollama client
  - Parse response into `DraftEmail` model:
    - `to: str` (sender from original email)
    - `subject: str` (re: original subject)
    - `body: str` (drafted response)
    - `missing_fields: list[str]`
    - `ticket_id: UUID`
  - Log draft generation to AILog table
  - Return draft for user review
- Handle draft failures:
  - If LLM fails, generate a simple template draft
  - Always return a draft (never fail silently)

## Dependencies
- Task 4.1
- Task 4.2

## Acceptance Criteria
- Generates professional draft email
- Lists only missing fields
- Includes original sender and subject context
- Falls back to template on LLM failure
- Draft is logged to AILog
