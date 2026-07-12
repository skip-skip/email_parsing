# Task 6.5 — Missing Information Flow Tests

## Description
Write tests for the complete missing information flow.

## Status
Complete

## Subtasks
- Test email draft agent:
  - Test draft generation with sample data
  - Test fallback template on LLM failure
  - Test missing fields are listed correctly
- Test queue service:
  - Test adding items to queue
  - Test retrieving queue items
  - Test approval sends email
  - Test rejection removes item
  - Test draft editing
- Test API endpoints:
  - Test GET returns correct data
  - Test POST approval triggers email
  - Test POST rejection works
  - Test PUT updates draft
  - Test 404 for nonexistent ticket
- Test conversation handler:
  - Test reply merges information
  - Test ticket completes when all fields present
  - Test new draft generated for remaining missing fields

## Dependencies
- Task 6.1
- Task 6.2
- Task 6.3
- Task 6.4

## Acceptance Criteria
- All unit tests pass with mocked dependencies
- API integration tests pass
- Email sending is mocked in tests
- Test coverage >80%
