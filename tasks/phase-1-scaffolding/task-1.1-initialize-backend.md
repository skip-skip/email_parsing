# Task 1.1 — Initialize Backend Project

## Description
Create the backend Python project with proper packaging and configuration.

## Status
Complete

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

## Notes
- System has Python 3.14.6 installed; `.python-version` pins 3.12. Works with `>=3.12` constraint but tools enforcing the pin (pyenv, asdf) may fail if 3.12 is not installed.
- Architecture diagram shows `backend/` with subdirectories directly beneath it. Task spec uses `backend/app/` as the importable Python package. Implemented per task spec: uvicorn module path is `backend.app.main:app`.
- `uvicorn.exe`, `ruff.exe`, `pytest.exe` etc. installed in `AppData\Roaming\Python\Python314\Scripts` which is not on PATH. Must invoke via `python -m uvicorn`, `python -m ruff`, `python -m pytest`. Affects Task 1.4 (Makefile) and Task 1.8 (final testing).
- Flat layout: `pyproject.toml` lives at repo root, not inside `backend/`. `pip install -e .` installs from repo root. If backend-only packaging is needed later, may require a `src/` layout or moving `pyproject.toml` into `backend/`.
