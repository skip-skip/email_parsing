# Task 11.2 — Build Email Classification Agent

## Description
Create an agent that uses the LLM to determine whether an email is a real task request.

## Status
Complete

## Subtasks
- Create `backend/app/agents/email_classification_agent.py`:
  - `ClassificationResult` dataclass: `is_task: bool`, `category: str`, `confidence: float`, `reason: str`
  - `EmailClassificationAgent` class:
    - `__init__(self, ollama_client: OllamaClient | None = None)`
    - `async classify(sender, subject, body) -> ClassificationResult`
  - Use `OllamaClient.generate_json()` with classification prompt
  - Log classification to AILog table (same pattern as EmailParsingAgent)
  - Handle failures gracefully: return `is_task=True` on error (fail-open)
- Add unit tests in `backend/tests/agents/test_email_classification_agent.py`:
  - Task request email → `is_task=True`, `category="task_request"`
  - Newsletter → `is_task=False`, `category="newsletter"`
  - Notification → `is_task=False`, `category="notification"`
  - LLM failure → fallback to `is_task=True`
  - Empty/malformed response → fallback to `is_task=True`

## Dependencies
- Task 11.1
- Task 4.1 (OllamaClient)

## Acceptance Criteria
- Classifies emails into all defined categories
- Returns structured `ClassificationResult` dataclass
- Logs every classification to AILog table
- Failures default to `is_task=True` (fail-open)
- All unit tests pass
