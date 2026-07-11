# Epic 2 — Database Models & Schemas

## Goal
Define all database tables, relationships, and Alembic migrations so the application has a persistent data layer.

## Status
Complete

## Tasks
| Task | Title | Status | Dependencies |
|------|-------|--------|-------------|
| 2.1 | Ticket Model | Complete | 1.5 |
| 2.2 | Email Model | Complete | 1.5 |
| 2.3 | CalendarEvent Model | Complete | 1.5, 2.1 |
| 2.4 | AILog Model | Complete | 1.5 |
| 2.5 | Create Alembic Migration | Complete | 2.1–2.4 |
| 2.6 | Database Repository Layer | Complete | 2.1–2.4 |

## Acceptance Criteria
- All models map correctly to database tables
- Migrations apply and rollback cleanly
- Seed script populates dev database
- Repository methods work with async sessions
