# Task 11.6 — Write Integration Tests

## Description
Write integration tests that verify the end-to-end flow from email detection through classification, ticket creation, and workflow execution.

## Status
Not Started

## Subtasks
- Create `backend/tests/integration/test_email_to_ticket_flow.py`:
  - Test complete flow: email → classify → ticket → workflow → IN_PROGRESS
  - Test classification filtering: non-task email → no ticket created
  - Test duplicate handling: same email twice → only one ticket
  - Test conversation threading: reply on existing thread → routed to ConversationHandler
- Update `backend/tests/conftest.py` if needed for new fixtures
- Run full test suite to verify no regressions

## Dependencies
- Tasks 11.1–11.5

## Acceptance Criteria
- Integration tests cover all major flow paths
- All existing tests continue to pass
- No regressions in workflow, agent, or monitor behavior
