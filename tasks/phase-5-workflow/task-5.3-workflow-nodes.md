# Task 5.3 — Implement Workflow Nodes

## Description
Implement the logic for each workflow node.

## Status
Not Started

## Subtasks
- Create `backend/app/workflows/nodes/` directory
- Create `receive_email.py`:
  - Triggered by monitor
  - Creates ticket in NEW status
  - Returns `WorkflowState` with ticket_id
- Create `extract_task.py`:
  - Calls `EmailParsingAgent`
  - Stores parsed data in state
  - Transitions ticket to PARSED
- Create `validate_fields.py`:
  - Runs deterministic validation rules
  - Checks required fields: task_description, project_number, budget_hours, deadline
  - Returns validation result with missing fields list
  - Transitions ticket to VALIDATED
- Create `route_by_validation.py`:
  - Reads validation result
  - Routes to missing info or scheduling path
  - Transitions ticket to appropriate status
- Create `draft_missing_info_email.py`:
  - Calls LLM to draft email requesting missing info
  - Stores draft in state
  - Transitions ticket to WAITING_FOR_INFORMATION
- Create `plan_schedule.py`:
  - Calls Calendar Planning Agent
  - Stores suggested blocks in state
  - Transitions ticket to READY_FOR_SCHEDULING
- Create `create_calendar_event.py`:
  - Calls CalendarManager to create Outlook events
  - Stores event IDs
  - Transitions ticket to CALENDAR_CREATED
- Create `dispatch_task.py`:
  - Marks ticket as ready for execution
  - Transitions ticket to IN_PROGRESS

## Dependencies
- Task 4.4
- Task 4.1
- Task 3.2

## Acceptance Criteria
- Each node performs exactly one business function
- Nodes communicate only through `WorkflowState`
- No node directly modifies system state (only state manager does)
- All nodes are independently testable
