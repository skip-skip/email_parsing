# Task 1.5 — Set Up Database Infrastructure

## Description
Configure SQLAlchemy, database connection, and migration tooling.

## Status
Complete

## Subtasks
- Install SQLAlchemy, Alembic, aiosqlite (dev), asyncpg (prod)
- Create `backend/app/services/database/` directory
- Create `database.py` with async engine and session factory
- Create `base.py` with declarative base class
- Initialize Alembic with `alembic init`
- Configure Alembic for async SQLAlchemy
- Create first migration (empty, for baseline)
- Add database startup/shutdown events to FastAPI app

## Dependencies
- Task 1.1

## Acceptance Criteria
- `alembic upgrade head` creates the database
- FastAPI app connects to database on startup
- Session dependency works in route handlers
