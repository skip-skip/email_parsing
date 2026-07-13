# Task 11.4 — Build Email Processor Service (Bridge)

## Description
Create the bridge service that connects the email monitor to the workflow. After the monitor stores a new email, the processor classifies it, creates a ticket if it's a task, and invokes the LangGraph workflow.

## Status
Not Started

## Subtasks
- Create `backend/app/services/email_processor.py`:
  - `ProcessingResult` dataclass: `email_id`, `ticket_id`, `is_task`, `classification`, `workflow_status`, `error`
  - `EmailProcessor` class:
    - `__init__(self, classification_agent, intake_agent)`
    - `async process_new_email(message: OutlookEmailMessage) -> ProcessingResult`
  - Flow:
    1. Classify email via `EmailClassificationAgent.classify()`
    2. If `is_task == False` → log classification, return early with `is_task=False`
    3. Create `Ticket` via `TicketRepository.create()` with status `NEW`
       - `client`: "Unknown" (will be refined by LLM extraction)
       - `contact`: sender email
       - `task_description`: subject line
       - `conversation_id`: from message
    4. Link email to ticket via `EmailRepository.update()`
    5. Build initial `WorkflowState` dict with ticket_id + sender/subject/body
    6. Invoke `compile_workflow().ainvoke(state)` via `asyncio.to_thread()` (workflow nodes use `asyncio.run()` internally)
    7. Return `ProcessingResult` with final status
- Handle edge cases:
  - Duplicate email (already processed) → return early
  - LLM classification failure → fail-open, process as task
  - Workflow invocation failure → log error, return error in result
  - Ticket creation failure → log error, return error in result
- Write unit tests in `backend/tests/services/test_email_processor.py`:
  - Full flow: classify → create ticket → invoke workflow → success
  - Skip path: classify → not a task → no ticket created
  - Duplicate email → no duplicate ticket
  - Classification failure → fail-open, processes anyway
  - Workflow failure → error returned in result

## Dependencies
- Task 11.2 (classification agent)
- Task 11.3 (workflow state)
- Task 4.3 (email intake agent)
- Task 2.6 (repositories)

## Acceptance Criteria
- Creates Ticket records for task emails
- Links email records to tickets
- Invokes LangGraph workflow with correct initial state
- Skips non-task emails without creating tickets
- Handles duplicates, LLM failures, and workflow failures gracefully
- All unit tests pass
