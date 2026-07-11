# Task 1.1 — Initialize Backend Project

## Description
Create the backend Python project with proper packaging and configuration.

## Status
Not Started

## Subtasks
- Create `backend/` directory structure matching architecture
- Initialize `pyproject.toml` with project metadata and dependencies
- Add `.python-version` file (Python 3.12)
- Create `backend/app/__init__.py`
- Create `backend/app/main.py` with FastAPI app instance and health check endpoint
- Add `uvicorn` runner configuration

## Dependencies
None

## Acceptance Criteria
- `uvicorn backend.app.main:app` starts without errors
- `GET /health` returns `{"status": "ok"}`
