.PHONY: help all setup env install config migrate model check-python check-node \
       dev dev-backend dev-frontend \
       lint lint-python lint-frontend \
       test test-python test-coverage \
       db-migrate db-seed db-verify db-reset

# ──────────────────────────────────────────────
#  Help
# ──────────────────────────────────────────────

help: ## Show this help
	@echo.
	@echo  AI Task Manager - Make Targets
	@echo  ───────────────────────────────
	@echo.
	@echo  Setup:
	@echo    make all           Everything from a fresh clone (start here)
	@echo    make setup         Install deps + migrate (run after conda activate)
	@echo    make env           Create conda environment
	@echo    make install       Install Python + Node dependencies
	@echo    make config        Create .env (only if missing)
	@echo    make migrate       Run database migrations
	@echo    make model         Pull default Ollama model
	@echo.
	@echo  Development:
	@echo    make dev           Run backend with auto-reload
	@echo    make dev-frontend  Run frontend dev server
	@echo.
	@echo  Quality:
	@echo    make lint          Lint + type-check all code
	@echo    make test          Run Python test suite
	@echo    make test-coverage Run tests with coverage
	@echo.
	@echo  Database:
	@echo    make db-migrate    Run pending migrations
	@echo    make db-seed       Seed with test data
	@echo    make db-verify     Verify migrations apply/rollback
	@echo    make db-reset      Reset database (deletes data)
	@echo.

# ──────────────────────────────────────────────
#  Full setup (fresh machine)
# ──────────────────────────────────────────────

all: env config model ## Everything from a fresh clone — then run the two commands below
	@echo.
	@echo  ------------------------------------------------------
	@echo  Two commands left. Paste them into your terminal:
	@echo.
	@echo    conda activate ai-task-manager
	@echo    make setup
	@echo.
	@echo  That will install all dependencies and run migrations.
	@echo  ------------------------------------------------------

# ──────────────────────────────────────────────
#  Setup (after conda activate)
# ──────────────────────────────────────────────

setup: install config migrate ## Install deps + migrate (run after conda activate)
	@echo.
	@echo  Setup complete. Run 'make help' to see available targets.

env: ## Create conda environment (safe if already exists)
	@where conda >nul 2>&1 || (echo  ERROR: conda not found. && exit 1)
	@conda env list | findstr /C:"ai-task-manager" >nul 2>&1 && echo  Environment 'ai-task-manager' already exists, skipping. || (echo  Creating conda environment... && conda env create -f environment.yml)
	@echo  Activate it with:  conda activate ai-task-manager

install: ## Install Python and Node.js dependencies
	@echo  Installing Python dependencies...
	@pip install -e ".[dev]" --quiet
	@echo  Installing frontend dependencies...
	@cd frontend && npm install --silent
	@echo  Dependencies installed.

config: ## Create .env from .env.example (only if .env does not exist)
	@if exist .env (echo  .env already exists, skipping.) else (copy .env.example .env >nul && echo  Created .env from .env.example. Edit it to match your setup.)

migrate: ## Run database migrations
	@echo  Running database migrations...
	@python -m alembic upgrade head
	@echo  Migrations complete.

model: ## Pull default Ollama model (safe if already exists)
	@where ollama >nul 2>&1 && (echo  Pulling ollama model qwen3:8b... && ollama pull qwen3:8b) || echo  Ollama not found — skipping. Install from https://ollama.com and run 'make model' later.

# ──────────────────────────────────────────────
#  Guard checks
# ──────────────────────────────────────────────

check-python:
	@where python >nul 2>&1 || (echo  ERROR: python not found. Activate your conda environment first. && exit 1)

check-node:
	@where node >nul 2>&1 || (echo  ERROR: node not found. Install from https://nodejs.org && exit 1)

# ──────────────────────────────────────────────
#  Development
# ──────────────────────────────────────────────

dev: dev-backend

dev-backend: check-python ## Run backend with auto-reload
	python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload

dev-frontend: check-node ## Run frontend dev server
	cd frontend && npm run dev

# ──────────────────────────────────────────────
#  Linting
# ──────────────────────────────────────────────

lint: lint-python lint-frontend

lint-python: check-python ## Lint and type-check Python code
	python -m ruff check backend/ shared/
	python -m ruff format --check backend/ shared/
	python -m mypy backend/ shared/schemas/

lint-frontend: check-node ## Lint TypeScript code
	cd frontend && npm run lint

# ──────────────────────────────────────────────
#  Testing
# ──────────────────────────────────────────────

test: test-python

test-python: check-python ## Run Python test suite
	python -m pytest

test-coverage: check-python ## Run tests with coverage report
	python -m pytest --cov=backend --cov-report=term-missing

# ──────────────────────────────────────────────
#  Database
# ──────────────────────────────────────────────

db-migrate: check-python ## Run pending database migrations
	python -m alembic upgrade head

db-seed: check-python ## Seed database with test data
	python -m backend.app.seed

db-verify: check-python ## Verify all migrations apply and rollback cleanly
	python -m backend.app.verify_migrations

db-reset: check-python ## Reset database (WARNING: deletes all data)
	python -m backend.app.reset_db
