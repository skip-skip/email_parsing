# Task 4.6 — Agent Integration Tests

## Description
Write tests for the intake and parsing agents.

## Status
Not Started

## Subtasks
- Create `backend/tests/agents/`
- Test `EmailIntakeAgent`:
  - Test new email storage
  - Test duplicate detection
  - Test conversation linking
- Test `EmailParsingAgent`:
  - Test extraction with sample emails (mock LLM)
  - Test JSON parsing failure handling
  - Test confidence calculation
  - Test logging to AILog
- Test `ConversationTracker`:
  - Test field merging logic
  - Test no-op when no new information
  - Test multiple field updates
- Create fixture data with realistic email samples

## Dependencies
- Task 4.3
- Task 4.4
- Task 4.5

## Acceptance Criteria
- All unit tests pass with mocked LLM
- No tests require real Ollama instance
- Test coverage >80% for agents module
