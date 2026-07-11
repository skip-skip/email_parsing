# Epic 2 — Database Models & Schemas

## Goal
Define all database tables, relationships, and Alembic migrations so the application has a persistent data layer.

## Status
Not Started

## Tasks
| Task | Title | Status | Dependencies |
|------|-------|--------|-------------|
| 2.1 | Ticket Model | Not Started | 1.5 |
| 2.2 | Email Model | Not Started | 1.5 |
| 2.3 | CalendarEvent Model | Not Started | 1.5, 2.1 |
| 2.4 | AILog Model | Not Started | 1.5 |
| 2.5 | Create Alembic Migration | Not Started | 2.1–2.4 |
| 2.6 | Database Repository Layer | Not Started | 2.1–2.4 |

## Acceptance Criteria
- All models map correctly to database tables
- Migrations apply and rollback cleanly
- Seed script populates dev database
- Repository methods work with async sessions
