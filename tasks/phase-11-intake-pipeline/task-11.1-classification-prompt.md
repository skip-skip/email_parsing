# Task 11.1 — Create Email Classification Prompt

## Description
Create an LLM prompt that classifies incoming emails as task requests or non-task emails (newsletters, notifications, spam, etc.).

## Status
Not Started

## Subtasks
- Create `backend/app/prompts/email_classification.py`:
  - `EMAIL_CLASSIFICATION_VERSION` constant
  - `EMAIL_CLASSIFICATION_SYSTEM` — instructs LLM to return JSON with `is_task`, `category`, `confidence`, `reason`
  - `EMAIL_CLASSIFICATION_USER` — template with `{sender}`, `{subject}`, `{body}` placeholders
  - Categories: `task_request`, `informational`, `newsletter`, `notification`, `spam`, `other`
- Export new constants from `backend/app/prompts/__init__.py`

## Dependencies
None

## Acceptance Criteria
- Prompt produces valid JSON with all required fields
- Categories cover all common email types
- User prompt includes sender, subject, and body context
- Constants are exported from prompts package
