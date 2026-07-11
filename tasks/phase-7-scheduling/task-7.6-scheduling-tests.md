# Task 7.6 — Scheduling Flow Tests

## Description
Write tests for the complete scheduling flow.

## Status
Not Started

## Subtasks
- Test calendar planning agent:
  - Test suggestion generation with sample data
  - Test validation of suggestions (hours, deadline, conflicts)
  - Test logging to AILog
- Test scheduling queue:
  - Test adding items to queue
  - Test retrieving queue items
  - Test approval creates events
  - Test decline sends email
  - Test modification updates blocks
- Test API endpoints:
  - Test GET returns correct data
  - Test POST approval creates events
  - Test POST decline works
  - Test POST modification works
  - Test calendar availability endpoint
- Test calendar manager:
  - Test event creation
  - Test event update
  - Test event cancellation
  - Test timezone handling

## Dependencies
- Task 7.1
- Task 7.2
- Task 7.3
- Task 7.4
- Task 7.5

## Acceptance Criteria
- All unit tests pass with mocked dependencies
- Outlook COM calls are mocked
- Test coverage >80%
