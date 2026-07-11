# Task 2.5 — Create Alembic Migration

## Description
Generate and verify the initial migration containing all models.

## Status
Not Started

## Subtasks
- Import all models in a central `models/__init__.py`
- Run `alembic revision --autogenerate -m "initial schema"`
- Review generated migration for correctness
- Verify migration applies cleanly: `alembic upgrade head`
- Verify rollback works: `alembic downgrade -1` then `alembic upgrade head`
- Add seed data script for development (sample ticket, sample email)

## Dependencies
- Task 2.1
- Task 2.2
- Task 2.3
- Task 2.4

## Acceptance Criteria
- Migration applies without errors
- All tables, columns, indexes, and foreign keys created correctly
- Seed script populates dev database with sample data
