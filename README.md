# AI Task Manager

A local-first AI task management assistant that monitors Microsoft Outlook, extracts actionable tasks from emails, manages scheduling, and prepares work for downstream AI systems — all while keeping you in full control.

## Key Features

- **Outlook Integration** — Automatically monitors your inbox for new emails and extracts task-relevant information using AI
- **AI-Powered Parsing** — Uses locally hosted LLMs (Ollama) to extract client names, deadlines, project numbers, and budgeted hours from emails
- **Missing Information Flow** — Drafts follow-up emails to request missing details; you review and approve before sending
- **Calendar Scheduling** — Analyzes your Outlook calendar and suggests work blocks that fit within deadlines
- **Review Dashboard** — React-based UI for reviewing parsed tasks, approving drafts, and managing schedules
- **Full Audit Trail** — Every AI interaction is logged with model, prompt version, confidence, and execution time
- **Local-First** — No cloud dependencies; runs entirely on your Windows workstation with locally hosted LLMs

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Backend | Python 3.12+, FastAPI, SQLAlchemy, Alembic |
| Frontend | React 19, TypeScript, Vite, TanStack Query, Zustand, Tailwind CSS |
| Workflow | LangGraph |
| Local AI | Ollama (Qwen 3, Gemma 3, Llama 3) |
| Database | SQLite (dev) / PostgreSQL (production) |
| Outlook | pywin32 COM Automation |
| Scheduling | APScheduler |
| Containerization | Docker, Docker Compose |

## Quick Start

### Prerequisites

- Windows 10/11
- [Miniconda](https://docs.conda.io/en/latest/miniconda.html) or [Anaconda](https://www.anaconda.com/download)
- [Node.js 18+](https://nodejs.org)
- [Ollama](https://ollama.com/)
- Outlook Desktop (for email/calendar integration)

### One-command setup

```bash
git clone <repository-url>
cd email_parsing
conda activate ai-task-manager   # create env first with: conda env create -f environment.yml
make setup
```

`make setup` runs everything: installs Python + Node dependencies, creates `.env` if missing, runs database migrations, and pulls the default Ollama model.

### Start the app

```bash
make dev-backend     # API at http://127.0.0.1:8000
make dev-frontend    # Dashboard at http://localhost:5173
```

### Verify

Open http://127.0.0.1:8000/health — you should see:

```json
{"status": "ok"}
```

The dashboard is available at http://localhost:5173 when running the frontend dev server.

Run `make help` to see all available targets.

## Environment Variables

Copy `.env.example` to `.env` and configure:

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | SQLAlchemy database URL | `sqlite+aiosqlite:///./data.db` |
| `OLLAMA_BASE_URL` | Ollama API base URL | `http://localhost:11434` |
| `POLL_INTERVAL_SECONDS` | Outlook inbox poll interval | `30` |
| `LOG_LEVEL` | Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL) | `INFO` |
| `OUTLOOK_ENABLED` | Enable/disable Outlook polling | `true` |
| `POSTGRES_USER` | PostgreSQL username (Docker) | `aitaskmanager` |
| `POSTGRES_PASSWORD` | PostgreSQL password (Docker) | `aitaskmanager` |
| `POSTGRES_DB` | PostgreSQL database name (Docker) | `aitaskmanager` |

## Docker Deployment

For production-like deployment with PostgreSQL:

```bash
# Copy and configure environment
copy .env.example .env

# Start all services
docker compose up -d

# Check status
docker compose ps
```

This starts:

- **db** — PostgreSQL 16 on port 5432
- **backend** — FastAPI application on port 8000

## Development

Run `make help` to see all available targets. Common commands:

```bash
make dev-backend     # Run backend with auto-reload
make dev-frontend    # Run frontend dev server
make lint            # Lint Python + TypeScript
make test            # Run Python test suite
make db-seed         # Seed database with test data
```

## Project Structure

```
email_parsing/
├── backend/
│   └── app/
│       ├── api/              # FastAPI route handlers
│       │   ├── tickets.py    # Active ticket CRUD
│       │   ├── queues.py     # Missing info queue
│       │   ├── scheduling.py # Scheduling queue
│       │   ├── ai_logs.py    # AI interaction logs
│       │   ├── logs.py       # Application logs
│       │   ├── llm.py        # LLM health & status
│       │   └── error_handlers.py
│       ├── agents/           # AI agents
│       │   ├── email_intake_agent.py
│       │   ├── email_parsing_agent.py
│       │   ├── email_draft_agent.py
│       │   ├── calendar_planning_agent.py
│       │   ├── acceptance_email_agent.py
│       │   └── conversation_tracker.py
│       ├── workflows/        # LangGraph workflow
│       │   ├── graph.py      # Workflow graph definition
│       │   ├── states.py     # State type definitions
│       │   └── nodes/        # Individual workflow nodes
│       ├── services/         # Core services
│       │   ├── outlook/      # Outlook COM integration
│       │   ├── llm/          # Ollama client & model management
│       │   ├── database/     # SQLAlchemy setup & repositories
│       │   ├── queues/       # Queue management
│       │   ├── scheduler/    # APScheduler setup
│       │   ├── validation/   # Ticket field validation
│       │   ├── logging.py    # Structured logging setup
│       │   └── errors.py     # Application error classes
│       ├── models/           # SQLAlchemy ORM models
│       ├── prompts/          # LLM prompt templates
│       └── main.py           # FastAPI application entry
├── frontend/                 # React + TypeScript dashboard
│   └── src/
│       ├── pages/            # Route pages
│       ├── components/       # UI components
│       ├── hooks/            # Custom React hooks
│       ├── stores/           # Zustand state stores
│       └── services/         # API client functions
├── shared/                   # Shared schemas and types
├── tasks/                    # Implementation task tracking
├── docs/                     # Project documentation
├── environment.yml           # Conda environment definition
├── pyproject.toml            # Python project configuration
├── docker-compose.yml        # Docker Compose services
└── ARCHITECTURE.md           # System architecture documentation
```

## How It Works

### Workflow

1. **Email Intake** — APScheduler polls Outlook every N seconds. New emails are detected and stored in the database.
2. **AI Parsing** — The Email Parsing Agent uses a local LLM to extract client, project number, deadline, budgeted hours, and other fields.
3. **Validation** — Deterministic rules check that all required fields are present. Missing fields trigger the Missing Information flow; complete tickets move to Scheduling.
4. **Missing Information** — The Email Draft Agent generates a follow-up email requesting the missing details. You review and approve before sending.
5. **Calendar Planning** — The Scheduling Agent queries your Outlook calendar, checks availability, and suggests work blocks that fit the deadline.
6. **User Approval** — You accept, modify, or decline the suggested schedule. Nothing happens automatically.
7. **Calendar Creation** — On approval, the system creates Outlook calendar appointments linked to the ticket.
8. **Task Dispatch** — Accepted work is handed off to the task execution system.

### Ticket Lifecycle

```
NEW → PARSED → VALIDATED → WAITING_FOR_INFORMATION → READY_FOR_SCHEDULING
    → PENDING_USER_APPROVAL → ACCEPTED → CALENDAR_CREATED
    → IN_PROGRESS → COMPLETED → ARCHIVED
```

## API Overview

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Application health check |
| `GET` | `/api/tickets/active` | List active tickets (ACCEPTED, CALENDAR_CREATED, IN_PROGRESS) |
| `GET` | `/api/tickets/{id}` | Get ticket details with calendar events |
| `GET` | `/api/queues/missing-info` | List missing information queue items |
| `GET` | `/api/queues/missing-info/{id}` | Get single missing info item |
| `POST` | `/api/queues/missing-info/{id}/approve` | Approve and send draft email |
| `POST` | `/api/queues/missing-info/{id}/reject` | Reject draft |
| `PUT` | `/api/queues/missing-info/{id}/draft` | Update draft email content |
| `GET` | `/api/scheduling/queue` | List scheduling queue items |
| `GET` | `/api/scheduling/queue/{id}` | Get single scheduling item |
| `POST` | `/api/scheduling/queue/{id}/approve` | Approve schedule |
| `POST` | `/api/scheduling/queue/{id}/decline` | Decline schedule |
| `POST` | `/api/scheduling/queue/{id}/modify` | Modify schedule blocks |
| `GET` | `/api/ai-logs` | List AI interaction logs (paginated) |
| `GET` | `/api/ai-logs/stats` | AI log statistics |
| `GET` | `/api/ai-logs/{ticket_id}` | AI logs for a specific ticket |
| `GET` | `/api/llm/health` | LLM model health status |
| `GET` | `/api/logs/app` | Application logs (paginated) |
| `GET` | `/api/logs/requests` | HTTP request logs (paginated) |
| `GET` | `/api/logs/stats` | Log statistics by level |

For full API documentation, see [docs/api.md](docs/api.md).

## Documentation

- [Setup Guide](docs/setup.md) — Clean machine setup instructions
- [Architecture](docs/architecture.md) — System architecture and design decisions
- [API Reference](docs/api.md) — Complete REST API documentation
- [ARCHITECTURE.md](ARCHITECTURE.md) — Original architecture document

## License

Private project — not for distribution.
