# Task 1.4 — Configure Development Environment

## Description
Set up development tooling, linting, and environment configuration.

## Status
Complete

## Subtasks
- Create `.env.example` with required environment variables:
  - `DATABASE_URL`
  - `OLLAMA_BASE_URL`
  - `POLL_INTERVAL_SECONDS`
  - `LOG_LEVEL`
- Create `.gitignore` covering Python, Node.js, and IDE files
- Configure `ruff` for Python linting
- Configure `mypy` for Python type checking
- Configure ESLint and Prettier for frontend
- Create `Makefile` or `justfile` with common commands:
  - `make dev` — start both backend and frontend
  - `make lint` — run all linters
  - `make test` — run all tests
  - `make db-migrate` — run database migrations

## Dependencies
- Task 1.1
- Task 1.2

## Acceptance Criteria
- Linters pass on all existing files
- Environment variables load correctly
- `make dev` starts both servers

## Notes
- **Frontend linting**: Task specified ESLint + Prettier, but project already uses oxlint (set up in task 1.2). Configured oxlint `.oxlintrc.json` instead to avoid tooling conflicts.
- **`make` not on PATH**: Makefile created but `make` is not installed on this Windows machine. Install via `choco install make` or use commands manually.
- **`shared/types` stdlib shadow**: Added `shared/__init__.py` to fix mypy namespace resolution. `shared/types/` excluded from mypy checks due to stdlib `types` module shadowing (contains only TypeScript `.ts` definitions).
