# AI Task Management System

## Architecture & Implementation Rules (Version 2.0 – Outlook Desktop Edition)

---

# Project Vision

Develop a **local-first AI task management assistant** that runs entirely on a Windows workstation. The assistant will monitor Outlook, extract actionable tasks from emails, manage scheduling, and prepare work for downstream AI systems while keeping the user in full control of all external actions.

This version intentionally avoids cloud dependencies wherever practical.

---

# Design Goals

1. Run entirely on a local Windows PC.
2. Use free and open-source software.
3. Use locally hosted LLMs.
4. Require no Azure subscription or Microsoft Graph integration.
5. Keep all business logic deterministic.
6. Require explicit user approval before any external action.

---

# System Philosophy

The system is composed of **specialized services** coordinated through a workflow engine.

The AI performs reasoning.

The application performs execution.

Never allow an LLM to directly modify system state.

---

# High-Level Architecture

```text
                           Outlook Desktop
                                  │
                     Windows COM Automation (pywin32)
                                  │
                     Outlook Integration Service
                                  │
                        LangGraph Workflow Engine
                                  │
      ┌──────────────┬──────────────┬──────────────┐
      │              │              │
 Email Intake   Scheduling    Future Task Execution
     Agent          Agent             Agent
      │              │
      └──────────────┴──────────────┐
                                    │
                              SQLite/PostgreSQL
                                    │
                             React Review Dashboard
                                    │
                              FastAPI Backend
                                    │
                             Ollama Local Models
```

---

# Core Components

## 1. Outlook Integration Service

Technology

* Python
* pywin32
* Outlook COM API

Responsibilities

* Monitor Inbox
* Detect new mail
* Retrieve attachments
* Retrieve conversation IDs
* Send replies
* Read Calendar
* Create calendar appointments
* Update calendar events

The remainder of the application should never interact directly with COM objects. This service acts as an abstraction layer.

---

## 2. Workflow Engine

Technology

* LangGraph

Responsibilities

Coordinate all workflow states.

Each node performs a single task.

Example nodes:

```text
Receive Email

↓

Extract Task

↓

Validate Fields

↓

Missing Info?

↓

Draft Email

↓

Wait

↓

Schedule

↓

Approve

↓

Create Calendar Event

↓

Dispatch Task
```

No node may perform more than one business function.

---

## 3. Local LLM Service

Technology

* Ollama

Recommended models

* Qwen 3 8B
* Gemma 3 12B
* Llama 3.3 8B

Responsibilities

* Task extraction
* Entity recognition
* Deadline interpretation
* Email drafting
* Conversation summarization
* Confidence estimation

The model never performs database writes or Outlook actions.

---

## 4. FastAPI Backend

Responsibilities

Provide REST endpoints for:

* Dashboard
* Review queues
* Ticket management
* Scheduling
* Logs
* Future integrations

Business logic belongs in services, not route handlers.

---

## 5. Review Dashboard

Technology

* React + TypeScript
* Vite (build tool)
* React Router v6 (routing)
* TanStack Query (server state, polling, caching)
* Zustand (client state)
* Tailwind CSS + shadcn/ui (styling, components)

Provides:

### Missing Information Queue

Shows:

* Original email
* Parsed fields
* Missing fields
* Draft response

Buttons:

* Edit
* Approve & Send
* Reject Draft

---

### Scheduling Queue

Shows:

* Ticket details
* Calendar availability
* Suggested work blocks
* Draft acceptance email

Buttons:

* Accept
* Decline
* Modify Schedule

---

### Active Tasks

Displays:

* Accepted work
* Calendar links
* Deadlines
* Progress

---

# Workflow

## Stage 1 — Outlook Monitor

A background service using APScheduler polls the Outlook inbox every N seconds (configurable, default 30s) and detects unread mail.

The email is stored in the database.

The workflow begins.

---

## Stage 2 — Email Parsing

The Email Parsing Agent extracts:

* client
* sender
* subject
* project number
* requested work
* deadline
* budget hours
* referenced attachments
* confidence

Output is structured JSON.

---

## Stage 3 — Validation

Deterministic rules verify required fields.

Required:

* Task description
* Project number
* Budgeted hours
* Deadline

If incomplete:

→ Missing Information Queue

Otherwise:

→ Scheduling Queue

---

## Stage 4 — Missing Information Queue

The Email Draft Agent prepares a response requesting only the missing information.

The user reviews:

* draft
* extracted fields
* missing fields

Approval triggers Outlook COM to send the email.

---

## Stage 5 — Conversation Tracking

Incoming replies are associated with the existing ticket using Outlook conversation identifiers.

New information is merged.

When complete:

Move to Scheduling Queue.

---

## Stage 6 — Calendar Planning

The Scheduling Agent queries Outlook Calendar.

Inputs:

* Existing appointments
* Existing accepted work
* Budgeted hours
* Deadline

Outputs:

Suggested schedule blocks.

Example:

```text
Tuesday
9:00–12:00

Wednesday
1:00–4:00
```

The Scheduling Agent also drafts an acceptance (or, if appropriate, a decline) email.

---

## Stage 7 — User Approval

User chooses:

* Accept
* Modify
* Decline

Nothing occurs automatically.

---

## Stage 8 — Calendar Creation

Upon approval:

Outlook COM:

* creates appointments
* links appointments to ticket
* stores event identifiers

---

## Stage 9 — Task Dispatch

Accepted work is transferred to the future Task Execution System.

---

# Ticket Lifecycle

```text
NEW

↓

PARSED

↓

VALIDATED

↓

WAITING_FOR_INFORMATION

↓

READY_FOR_SCHEDULING

↓

PENDING_USER_APPROVAL

↓

ACCEPTED

↓

CALENDAR_CREATED

↓

IN_PROGRESS

↓

COMPLETED

↓

ARCHIVED
```

State transitions are deterministic.

---

# Database

## Tickets

```text
ticket_id
status
client
contact
project_number
task_description
deadline
budget_hours
estimated_hours
priority
calendar_event_id
conversation_id
created_at
updated_at
```

---

## Emails

```text
email_id
conversation_id
entry_id
sender
subject
body
received_time
attachments
```

The Outlook `EntryID` uniquely identifies a message, while `ConversationID` groups related messages in the same thread.

---

## Calendar

```text
calendar_event_id
ticket_id
start_time
end_time
duration
status
```

---

## AI Logs

Store:

* model
* prompt version
* prompt
* response
* parsed JSON
* confidence
* execution time

This supports debugging and prompt refinement.

---

# Outlook Integration Layer

Implement a provider interface to isolate Outlook-specific code.

```python
class EmailProvider:
    def get_new_messages(self): ...
    def get_conversation(self, conversation_id): ...
    def send_reply(self, conversation_id, body): ...

class CalendarProvider:
    def get_events(self, start, end): ...
    def create_event(self, ticket): ...
    def update_event(self, event): ...
```

Then implement:

```text
OutlookComEmailProvider
OutlookComCalendarProvider
```

If you later migrate to Microsoft Graph or another service, only these provider implementations need to change.

---

# AI Responsibilities

Allowed:

* Extract task information.
* Summarize conversations.
* Interpret natural-language deadlines.
* Draft emails.
* Suggest schedules.
* Estimate confidence.

Forbidden:

* Writing to the database.
* Sending emails.
* Modifying Outlook.
* Changing ticket state.
* Applying business rules.

---

# Deterministic Rules

Examples:

```python
if ticket.project_number is None:
    status = WAITING_FOR_INFORMATION
```

```python
if ticket.deadline is None:
    status = WAITING_FOR_INFORMATION
```

```python
if ticket.budget_hours is None:
    status = WAITING_FOR_INFORMATION
```

LLMs never determine workflow transitions.

---

# Technology Stack

| Component           | Technology                                                    |
| ------------------- | ------------------------------------------------------------- |
| Language            | Python 3.12+                                                  |
| API                 | FastAPI                                                       |
| Frontend            | React + TypeScript, Vite, React Router v6, TanStack Query, Zustand, Tailwind CSS + shadcn/ui |
| Workflow            | LangGraph                                                     |
| Local AI            | Ollama                                                        |
| Models              | Qwen 3, Gemma 3, Llama 3                                      |
| Database            | PostgreSQL (production) / SQLite (development)                |
| ORM                 | SQLAlchemy                                                    |
| Validation          | Pydantic                                                      |
| Outlook Integration | pywin32 (COM Automation)                                      |
| Background Jobs     | APScheduler                                                   |
| Logging             | Loguru or Python `logging`                                    |
| Packaging           | Docker (backend) and Windows installer for desktop deployment |

---

# Project Structure

```text
ai-task-manager/
│
├── backend/
│   ├── api/
│   ├── agents/
│   ├── workflows/
│   ├── services/
│   │   ├── outlook/
│   │   ├── llm/
│   │   ├── scheduler/
│   │   ├── database/
│   │   ├── queues/
│   │   └── validation/
│   ├── models/
│   ├── prompts/
│   └── tests/
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── hooks/
│   │   ├── stores/
│   │   ├── services/
│   │   └── lib/
│   ├── public/
│   ├── index.html
│   ├── vite.config.ts
│   ├── tailwind.config.ts
│   └── package.json
│
├── shared/
│   ├── schemas/
│   └── types/
│
└── docs/
    ├── architecture.md
    ├── workflow.md
    ├── prompts.md
    └── api.md
```

## Future Evolution

Design every major component behind interfaces so that replacing Outlook COM with Microsoft Graph, or Ollama with another model provider, requires minimal changes. Likewise, keep task execution as a separate subsystem that consumes accepted tickets rather than embedding execution logic into the intake and scheduling workflow. This separation will let the platform evolve from a personal desktop assistant into a multi-user or cloud-hosted system without requiring a fundamental redesign.
