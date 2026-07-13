# Task 11.5 — Wire Monitor to Email Processor

## Description
Update the Outlook monitor to call the EmailProcessor after storing each new email, completing the pipeline from email detection to workflow execution.

## Status
Not Started

## Subtasks
- Update `backend/app/services/outlook/monitor.py`:
  - Import `EmailProcessor` and its dependencies
  - Instantiate `EmailProcessor` in `OutlookMonitor.__init__()`
  - In `_poll_async()`, after storing a new email via `email_repo.create()`, call `processor.process_new_email(msg)`
  - Log processing results (ticket created, classification, workflow status)
  - Ensure processor errors don't crash the poll loop (catch + log)
- Verify `OUTLOOK_ENABLED` env var still controls polling
- Test manually: send a task-request email → confirm ticket is created and workflow runs
- Test manually: send a newsletter → confirm no ticket is created

## Dependencies
- Task 11.4

## Acceptance Criteria
- New emails trigger classification and workflow processing
- Task emails create tickets and invoke the workflow
- Non-task emails are filtered without ticket creation
- Monitor poll loop is resilient to processor failures
- Manual testing confirms end-to-end flow works
