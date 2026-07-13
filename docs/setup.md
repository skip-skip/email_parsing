# Setup Guide

Step-by-step instructions for setting up the AI Task Manager on a clean Windows machine.

## Prerequisites

### Required Software

1. **Windows 10/11** — The application uses Outlook COM Automation, which requires Windows.

2. **Git** — [Download](https://git-scm.com/download/win)

3. **Miniconda or Anaconda** — [Download Miniconda](https://docs.conda.io/en/latest/miniconda.html) (recommended, smaller download)

4. **Ollama** — [Download](https://ollama.com/download) and install the Windows version.

5. **Microsoft Outlook Desktop** — Required for email monitoring and calendar integration. The Outlook desktop application must be installed and configured with a mailbox.

### Verify Prerequisites

Open PowerShell and run:

```powershell
git --version          # Should show git version
conda --version        # Should show conda version
ollama --version       # Should show ollama version
```

## Step 1: Clone the Repository

```powershell
git clone <repository-url>
cd email_parsing
```

## Step 2: Create the Conda Environment

```powershell
conda env create -f environment.yml
conda activate ai-task-manager
```

This creates an environment named `ai-task-manager` with Python 3.12 and all dependencies.

To update the environment after pulling new changes:

```powershell
conda env update -f environment.yml --prune
```

## Step 3: Pull Ollama Models

Start Ollama (it runs as a background service on install), then pull the recommended models:

```powershell
ollama pull qwen3:8b
```

The system supports a fallback chain of models. Pull additional models as desired:

```powershell
ollama pull gemma3:12b
ollama pull llama3.3:8b
```

Verify Ollama is running:

```powershell
ollama list
```

## Step 4: Configure Environment Variables

```powershell
copy .env.example .env
```

Edit `.env` with your preferred text editor:

```powershell
notepad .env
```

### Configuration Options

| Variable | Description | Default | Notes |
|----------|-------------|---------|-------|
| `DATABASE_URL` | SQLAlchemy database URL | `sqlite+aiosqlite:///./data.db` | Use the PostgreSQL URL for Docker |
| `OLLAMA_BASE_URL` | Ollama API endpoint | `http://localhost:11434` | Change if Ollama runs on a different port |
| `POLL_INTERVAL_SECONDS` | How often to check Outlook | `30` | Lower = more responsive, higher = less resource usage |
| `LOG_LEVEL` | Logging verbosity | `INFO` | Use `DEBUG` for troubleshooting |
| `OUTLOOK_ENABLED` | Enable Outlook polling | `true` | Set to `false` for testing without Outlook |
| `POSTGRES_USER` | PostgreSQL username (Docker) | `aitaskmanager` | Only used by Docker Compose |
| `POSTGRES_PASSWORD` | PostgreSQL password (Docker) | `aitaskmanager` | Only used by Docker Compose |
| `POSTGRES_DB` | PostgreSQL database name (Docker) | `aitaskmanager` | Only used by Docker Compose |

## Step 5: Start the Backend

```powershell
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
```

On first run, the application will:

1. Create the SQLite database file (`data.db`) in the project root
2. Run any pending migrations
3. Start the Outlook monitor (if Outlook is running)
4. Perform an initial LLM health check
5. Start the HTTP server on port 8000

You should see log output like:

```
Application startup complete
```

Verify the server is running:

```powershell
curl http://127.0.0.1:8000/health
```

Expected response:

```json
{"status": "ok"}
```

## Step 6: Start the Frontend (Optional)

The frontend provides a web-based dashboard for reviewing tasks.

```powershell
cd frontend
npm install
npm run dev
```

The dashboard is available at http://localhost:5173.

## Docker Setup (Alternative)

If you prefer Docker or want a PostgreSQL database:

### Start with Docker Compose

```powershell
docker compose up -d
```

This starts:

- **db** — PostgreSQL 16 on port 5432
- **backend** — FastAPI application on port 8000

The backend Docker container uses the PostgreSQL URL from your `.env` file. Make sure `DATABASE_URL` is set to:

```
DATABASE_URL=postgresql+asyncpg://aitaskmanager:aitaskmanager@db:5432/aitaskmanager
```

### View Logs

```powershell
docker compose logs -f backend
```

### Stop Services

```powershell
docker compose down
```

### Stop and Remove Data

```powershell
docker compose down -v
```

## Troubleshooting

### "Outlook monitor disabled via OUTLOOK_ENABLED=false"

Outlook polling is disabled. Set `OUTLOOK_ENABLED=true` in your `.env` and ensure Outlook Desktop is running.

### "Failed to connect to Ollama"

Ensure Ollama is running. Check by opening http://localhost:11434 in a browser. You should see "Ollama is running."

If Ollama is on a different port, update `OLLAMA_BASE_URL` in your `.env`.

### Database errors

For development with SQLite, the database file is created automatically. If you encounter issues, delete `data.db` and restart the backend — migrations will recreate the schema.

For PostgreSQL via Docker, ensure the `db` service is healthy:

```powershell
docker compose ps
```

### LLM health check shows "degraded"

At least one model in the fallback chain must be available. Pull the required models with `ollama pull <model-name>`.

### Port already in use

If port 8000 is occupied, specify a different port:

```powershell
python -m uvicorn backend.app.main:app --port 8001 --reload
```

## Running Tests

```powershell
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run a specific test file
pytest backend/tests/test_validation.py
```

## Code Quality

```powershell
# Lint
ruff check backend/

# Format check
ruff format --check backend/

# Type check
mypy backend/
```
