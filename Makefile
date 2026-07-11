.PHONY: dev dev-backend dev-frontend lint lint-python lint-frontend test test-python db-migrate install

# Development

dev: dev-backend

dev-backend:
	python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload

dev-frontend:
	cd frontend && npm run dev

# Linting

lint: lint-python lint-frontend

lint-python:
	python -m ruff check backend/ shared/
	python -m ruff format --check backend/ shared/
	python -m mypy backend/ shared/schemas/

lint-frontend:
	cd frontend && npm run lint

# Testing

test: test-python

test-python:
	python -m pytest

# Database

db-migrate:
	python -m alembic upgrade head

# Setup

install:
	pip install -e ".[dev]"
	cd frontend && npm install
