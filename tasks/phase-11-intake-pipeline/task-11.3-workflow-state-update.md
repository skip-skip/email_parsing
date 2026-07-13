# Task 11.3 — Update WorkflowState Schema

## Description
Add `sender`, `subject`, and `body` fields to the `WorkflowState` TypedDict so the workflow graph receives email metadata explicitly.

## Status
Complete

## Subtasks
- Update `backend/app/workflows/states.py`:
  - Add `sender: str` field to `WorkflowState`
  - Add `subject: str` field to `WorkflowState`
  - Add `body: str` field to `WorkflowState`
- Verify `extract_task` node (`backend/app/workflows/nodes/extract_task.py`) already reads these via `.get()` — no changes needed there
- Update existing integration tests that construct `WorkflowState` dicts:
  - `backend/tests/integration/test_complete_email_flow.py`
  - `backend/tests/integration/test_missing_info_flow.py`
  - `backend/tests/integration/test_scheduling_flow.py`
  - `backend/tests/workflows/test_workflow_graph.py`

## Dependencies
None

## Acceptance Criteria
- `WorkflowState` TypedDict includes `sender`, `subject`, `body`
- All existing tests pass with updated state dicts
- No behavior change — fields were already read via `.get()`, now declared explicitly
