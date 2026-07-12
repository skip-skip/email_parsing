# Task 4.2 — Create Prompt Templates

## Description
Define and version all prompt templates used by agents.

## Status
Complete

## Subtasks
- Create `backend/app/prompts/` directory
- Create `email_extraction.py`:
  - System prompt instructing the model to extract task fields from email
  - User prompt template with email body and subject
  - Output schema definition (JSON)
  - Prompt version string (e.g., `v1.0.0`)
- Create `missing_info_draft.py`:
  - System prompt for drafting a reply requesting missing information
  - User prompt template with ticket fields and missing field list
  - Prompt version string
- Create `schedule_suggestion.py`:
  - System prompt for suggesting calendar blocks
  - User prompt template with calendar availability, deadline, and hours
  - Prompt version string
- Create `conversation_summary.py`:
  - System prompt for summarizing email threads
  - User prompt template with conversation history
  - Prompt version string
- Store prompts as Python constants or in a `prompts/` directory with `.txt` files

## Dependencies
None

## Acceptance Criteria
- Each prompt has a unique version string
- Prompts produce valid JSON when tested with sample input
- Prompts are easy to read and modify
- No hardcoded prompts in agent code
