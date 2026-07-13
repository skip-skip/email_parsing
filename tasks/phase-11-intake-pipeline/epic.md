# Epic 11 — Email Intake Pipeline: Classification & Workflow Bridge

## Goal
Wire the Outlook email monitor to the LangGraph workflow so incoming emails are automatically classified as task requests and processed into tickets. Add LLM-based classification to filter non-task emails (newsletters, notifications, etc.) before ticket creation.

## Status
Not Started

## Tasks
| Task | Title | Status | Dependencies |
|------|-------|--------|-------------|
| 11.1 | Create Email Classification Prompt | Complete | None |
| 11.2 | Build Email Classification Agent | Complete | 11.1, 4.1 |
| 11.3 | Update WorkflowState Schema | Complete | None |
| 11.4 | Build Email Processor Service (Bridge) | Not Started | 11.2, 11.3, 4.3, 2.6 |
| 11.5 | Wire Monitor to Email Processor | Not Started | 11.4 |
| 11.6 | Write Integration Tests | Not Started | 11.1–11.5 |

## Architecture

```
Outlook Monitor (_poll_async)
  → Store email in DB (existing)
  → EmailProcessor.process_new_email(msg)
    → EmailClassificationAgent.classify(sender, subject, body)
      → If NOT a task → log + skip
      → If IS a task:
        → Create Ticket (status=NEW)
        → Link email to ticket
        → Invoke LangGraph workflow via ainvoke()
```

## Acceptance Criteria
- Emails are classified before ticket creation
- Non-task emails (newsletters, notifications, spam) are filtered out
- Task emails create a Ticket record and invoke the full workflow
- Classification failures default to processing (fail-open)
- All existing tests continue to pass
- New tests cover classification agent, processor service, and end-to-end flow
