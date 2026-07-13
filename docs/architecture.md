# Architecture

This document describes the system architecture, component responsibilities, and key design decisions for the AI Task Manager.

## Design Principles

1. **Local-First** — All processing happens on the local machine. No cloud APIs or external services required.
2. **AI Reasons, Application Executes** — LLMs perform extraction and drafting. The application handles all state changes, database writes, and external actions.
3. **User Approval Required** — No emails are sent, calendar events created, or tickets dispatched without explicit user confirmation.
4. **Interface-Based Abstraction** — External integrations (Outlook, LLM) are behind provider interfaces, enabling future replacement without cascading changes.

## System Overview

```
                         Outlook Desktop
                                |
                   Windows COM Automation (pywin32)
                                |
                   Outlook Integration Service
                                |
                      LangGraph Workflow Engine
                                |
      +--------------+--------------+--------------+
      |              |              |              |
 Email Intake   Email Parsing  Validation    Scheduling
    Agent          Agent          Rules         Agent
      |              |              |              |
      +--------------+--------------+--------------+
                                |
                          SQLite / PostgreSQL
                                |
                         FastAPI Backend
                          /           \
               React Dashboard    Ollama Local LLM
```

## Components

### 1. Outlook Integration Service

**Location:** `backend/app/services/outlook/`

**Purpose:** Abstracts all Outlook COM interactions behind provider interfaces.

**Key Files:**
- `base.py` — Abstract base classes `EmailProvider` and `CalendarProvider`
- `com_email_provider.py` — Outlook COM implementation for email operations
- `com_calendar_provider.py` — Outlook COM implementation for calendar operations
- `monitor.py` — APScheduler-based inbox polling service
- `models.py` — Data transfer objects (`EmailMessage`, `OutlookCalendarEvent`, `FreeBusyInfo`)

**Design:**
- The `OutlookMonitor` runs as a background scheduler that polls the Outlook inbox at a configurable interval (default 30s).
- New emails are detected by `EntryID` and stored in the database.
- The rest of the application never interacts with COM objects directly — only through these provider interfaces.
- Outlook can be disabled via `OUTLOOK_ENABLED=false` for development/testing without Outlook.

### 2. AI Agents

**Location:** `backend/app/agents/`

**Purpose:** Specialized agents that perform single AI-driven tasks using locally hosted LLMs.

| Agent | File | Responsibility |
|-------|------|---------------|
| Email Intake | `email_intake_agent.py` | Receives new emails, checks for duplicates, creates initial database records |
| Email Parsing | `email_parsing_agent.py` | Extracts structured fields (client, deadline, project number, etc.) from email text |
| Email Draft | `email_draft_agent.py` | Generates follow-up emails requesting missing information |
| Calendar Planning | `calendar_planning_agent.py` | Analyzes calendar availability and suggests work blocks |
| Acceptance Email | `acceptance_email_agent.py` | Drafts acceptance or decline emails after scheduling |
| Conversation Tracker | `conversation_tracker.py` | Associates reply emails with existing tickets via conversation IDs |

**Design:**
- Each agent wraps an LLM call with prompt templating, response parsing, and AI log recording.
- Agents never write to the database directly — they return data structures that the workflow engine processes.
- If an LLM call fails, agents return low-confidence fallback results rather than crashing the workflow.

### 3. Workflow Engine

**Location:** `backend/app/workflows/`

**Purpose:** Orchestrates the ticket lifecycle using LangGraph state machines.

**Key Files:**
- `graph.py` — Builds and compiles the LangGraph workflow graph
- `states.py` — TypedDict definitions for workflow state
- `transitions.py` — State transition logic
- `nodes/` — Individual workflow nodes (receive_email, extract_task, validate_fields, etc.)

**Workflow Graph:**

```
receive_email -> extract_task -> validate_fields
                                      |
                        +-------------+-------------+
                        |                           |
               (missing fields)            (all fields present)
                        |                           |
           draft_missing_info_email         plan_schedule
                   |                           |
                 END               create_calendar_event
                                           |
                                     dispatch_task
                                           |
                                         END
```

**Design:**
- Each node performs exactly one business function.
- Transitions are deterministic — no LLM determines workflow state changes.
- The workflow is defined as a `StateGraph` with typed state and compiled for execution.

### 4. Validation Engine

**Location:** `backend/app/services/validation/`

**Purpose:** Deterministic field validation that routes tickets to the correct queue.

**Key Files:**
- `field_rules.py` — Declarative field validation rules
- `validator.py` — `TicketValidator` class and `ValidationResult` dataclass

**Rules:**
- Required fields: `task_description`, `project_number`, `budget_hours`, `deadline`
- Optional constraints: minimum length, min/max values, custom validators
- Past deadlines generate warnings (not errors)

### 5. FastAPI Backend

**Location:** `backend/app/`

**Purpose:** REST API serving the React dashboard and external integrations.

**Key Directories:**
- `api/` — Route handlers organized by domain
- `services/database/` — SQLAlchemy setup, session management, and repository layer
- `services/queues/` — In-memory queue management for missing info and scheduling

**Design:**
- Business logic lives in services, not route handlers.
- All database access goes through the repository pattern.
- Structured logging with request IDs, slow request detection, and daily rotation.
- Centralized error handling with consistent JSON error responses.

### 6. React Dashboard

**Location:** `frontend/`

**Purpose:** Web-based UI for reviewing tasks, approving drafts, and managing schedules.

**Technology:** React 19, TypeScript, Vite, TanStack Query, Zustand, Tailwind CSS.

**Pages:**
- **Missing Information Queue** — Review and approve/reject draft emails for tickets with missing fields
- **Scheduling Queue** — Review AI-suggested schedules, accept/modify/decline
- **Active Tasks** — View accepted work with calendar links and deadlines
- **AI Logs** — Inspect AI interactions with filtering and statistics

**Design:**
- TanStack Query handles server state, polling, and caching.
- Zustand manages client-side state (filters, UI preferences).
- API calls go through a service layer with Axios.

### 7. LLM Service

**Location:** `backend/app/services/llm/`

**Purpose:** Manages Ollama integration with model fallback and health monitoring.

**Key Files:**
- `ollama_client.py` — HTTP client for Ollama API with retry logic
- `model_manager.py` — Fallback chain management, health checks, usage statistics
- `model_config.py` — Per-model configuration (temperature, top_p, num_predict)
- `ai_logger.py` — Structured logging of AI interactions to the database

**Design:**
- Configurable fallback chain: if the primary model fails, the system tries the next model automatically.
- Health checks run periodically to track model availability.
- All LLM interactions are logged with prompt version, response, confidence, and execution time.

### 8. Database

**Technology:** SQLAlchemy 2.0 with async support (aiosqlite for dev, asyncpg for production).

**Models:**
- `Ticket` — Core task record with status, fields, and relationships
- `Email` — Stored email messages linked to tickets via conversation IDs
- `CalendarEvent` — Calendar appointments linked to tickets
- `AILog` — AI interaction audit trail

**Design:**
- Repository pattern for all database operations.
- Alembic migrations for schema management.
- Async session management with proper cleanup.

## Data Flow

### Email Processing Flow

```
1. OutlookMonitor polls inbox
   |
2. New email detected (by EntryID)
   |
3. Email stored in database
   |
4. LangGraph workflow triggered
   |
5. EmailParsingAgent extracts fields via Ollama
   |
6. TicketValidator checks completeness
   |
7a. Missing fields -> MissingInfoQueue -> Draft generated -> User reviews
7b. All fields present -> SchedulingQueue -> Calendar planned -> User reviews
```

### Missing Information Flow

```
1. Ticket has missing required fields
   |
2. EmailDraftAgent generates follow-up email
   |
3. Draft stored in MissingInfoQueue
   |
4. User reviews in dashboard (edit, approve, or reject)
   |
5. On approval: Outlook sends reply email
   |
6. Reply received: ConversationTracker merges new info
   |
7. When complete: ticket moves to SchedulingQueue
```

### Scheduling Flow

```
1. Ticket is complete and validated
   |
2. CalendarPlanningAgent queries Outlook Calendar
   |
3. Agent suggests work blocks within deadline
   |
4. Suggestion stored in SchedulingQueue
   |
5. User reviews in dashboard (accept, modify, or decline)
   |
6. On approval: Outlook calendar appointments created
   |
7. Ticket moves to ACCEPTED -> CALENDAR_CREATED
```

## Ticket State Machine

```
NEW
 |  (email parsed)
 v
PARSED
 |  (fields validated)
 v
VALIDATED
 |  (has missing fields)
 v                                    v
WAITING_FOR_INFORMATION    READY_FOR_SCHEDULING
 |  (all info received)               |
 v                                    v
READY_FOR_SCHEDULING     PENDING_USER_APPROVAL
                                    |  (user approves)
                                    v
                               ACCEPTED
                                    |  (calendar created)
                                    v
                             CALENDAR_CREATED
                                    |  (work begins)
                                    v
                              IN_PROGRESS
                                    |  (work done)
                                    v
                               COMPLETED
                                    |  (archived)
                                    v
                               ARCHIVED
```

## Error Handling

All errors return a consistent JSON format:

```json
{
  "error": {
    "code": 404,
    "message": "Ticket not found"
  }
}
```

Error types are defined in `backend/app/services/errors.py`:

| Error Class | HTTP Status | Use Case |
|------------|-------------|----------|
| `NotFoundError` | 404 | Resource not found |
| `ValidationError` | 422 | Invalid request data |
| `ConflictError` | 409 | Resource state conflict |
| `ExternalServiceError` | 502 | Ollama/Outlook failure |
| `TransientError` | 503 | Temporary unavailability |
| `RateLimitError` | 429 | Rate limit exceeded |

The `retry` decorator in `errors.py` supports exponential backoff for transient failures on both sync and async callables.

## Logging

- **Structured JSON logs** via Loguru with daily rotation and 30-day retention
- **Request tracking** via X-Request-ID header (auto-generated if not provided)
- **Slow request detection** — requests exceeding 500ms are logged at WARNING level
- **AI audit trail** — every LLM interaction recorded in the `ai_logs` table with model, prompt version, response, confidence, and execution time

## Future Evolution

The system is designed for component-level replacement:

- **Outlook COM -> Microsoft Graph**: Replace `OutlookComEmailProvider` and `OutlookComCalendarProvider` with Graph API implementations. No other code changes needed.
- **Ollama -> Other LLM Provider**: Replace `OllamaClient` with a compatible client. The `ModelManager` handles fallback and health checks.
- **Single User -> Multi-User**: Add authentication middleware and user scoping to repositories.
- **Local -> Cloud**: Replace SQLite with PostgreSQL (already supported via Docker), add container orchestration.
