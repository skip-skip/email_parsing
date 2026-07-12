# Task 4.4 — Build Email Parsing Agent

## Description
Create the agent that uses the LLM to extract structured task information from emails.

## Status
Complete

## Subtasks
- Create `email_parsing_agent.py`:
  - Accept email body, subject, and sender
  - Call `email_extraction` prompt via Ollama client
  - Parse JSON response into `ParsedEmail` model
  - Validate extracted fields against Pydantic schema
  - Log extraction to AILog table (model, prompt, response, confidence, execution time)
  - Return `ParsedEmail` with confidence scores
- Handle extraction failures:
  - If JSON parsing fails, log error and return low-confidence result
  - If model refuses or returns empty, return low-confidence result
  - Never crash — always return a result (even with null fields)
- Add confidence calculation:
  - Per-field confidence (0.0–1.0)
  - Overall ticket confidence (average of field confidences)

## Dependencies
- Task 4.1
- Task 4.2
- Task 2.6

## Acceptance Criteria
- Extracts client, sender, subject, project_number, deadline, budget_hours, task_description, attachments
- All output conforms to `ParsedEmail` schema
- Every extraction is logged to AILog table
- Extraction failures return low-confidence result, not exceptions
- Per-field confidence scores are populated
