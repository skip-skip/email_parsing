# AI Task Manager

Local-first AI task management assistant that monitors Outlook, extracts actionable tasks from emails, manages scheduling, and prepares work for downstream AI systems.

## Prerequisites

- Windows 10/11
- [Miniconda](https://docs.conda.io/en/latest/miniconda.html) or [Anaconda](https://www.anaconda.com/download)
- Outlook Desktop (for email/calendar integration)

## Quick Start

### 1. Create the Conda Environment

```bash
conda env create -f environment.yml
conda activate ai-task-manager
```

### 2. Run the Backend

```bash
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
```

### 3. Verify

Open http://127.0.0.1:8000/health in your browser. You should see:

```json
{"status": "ok"}
```

## Environment Variables

Copy `.env.example` to `.env` and configure:

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | SQLAlchemy database URL | `sqlite+aiosqlite:///./data.db` |
| `OLLAMA_BASE_URL` | Ollama API base URL | `http://localhost:11434` |
| `POLL_INTERVAL_SECONDS` | Outlook inbox poll interval | `30` |
| `LOG_LEVEL` | Logging level | `INFO` |

## Development

```bash
# Start backend with auto-reload
python -m uvicorn backend.app.main:app --reload

# Run linter
python -m ruff check backend/

# Run type checker
python -m mypy backend/

# Run tests
python -m pytest
```

## Project Structure

```
ai-task-manager/
├── backend/
│   ├── app/
│   │   ├── api/            # FastAPI route handlers
│   │   ├── agents/         # AI agents (intake, parsing, scheduling)
│   │   ├── workflows/      # LangGraph workflow definitions
│   │   ├── services/       # Core services (outlook, llm, scheduler, database)
│   │   ├── models/         # SQLAlchemy ORM models
│   │   ├── prompts/        # LLM prompt templates
│   │   ├── queues/         # Queue management
│   │   └── main.py         # FastAPI application entry point
│   └── tests/
├── frontend/               # React + TypeScript dashboard
├── shared/                 # Shared schemas and types
├── tasks/                  # Implementation task tracking
├── environment.yml         # Conda environment definition
├── pyproject.toml          # Python project configuration
└── ARCHITECTURE.md         # System architecture documentation
```
