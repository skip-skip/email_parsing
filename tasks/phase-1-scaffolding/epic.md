# Epic 1 — Project Scaffolding & Core Infrastructure

## Goal
Set up the project structure, development environment, and core infrastructure so all subsequent phases have a foundation to build on.

## Status
In Progress

## Tasks
| Task | Title | Status | Dependencies |
|------|-------|--------|-------------|
| 1.1 | Initialize Backend Project | Complete | None |
| 1.2 | Initialize Frontend Project | Complete | None |
| 1.3 | Create Shared Schemas | Complete | 1.1, 1.2 |
| 1.4 | Configure Development Environment | Complete | 1.1, 1.2 |
| 1.5 | Set Up Database Infrastructure | Not Started | 1.1 |
| 1.6 | Set Up Logging | Not Started | 1.1 |

## Acceptance Criteria
- Backend starts with `uvicorn` and serves health check
- Frontend starts with Vite dev server
- Shared schemas validate on both sides
- Linters pass on all files
- Database migrations run cleanly
- Logging outputs to console and file
