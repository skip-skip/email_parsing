# Epic 7 — Scheduling Flow

## Goal
Implement the complete scheduling flow: calendar planning, user approval, and Outlook calendar creation.

## Status
Not Started

## Tasks
| Task | Title | Status | Dependencies |
|------|-------|--------|-------------|
| 7.1 | Build Calendar Planning Agent | Complete | 4.1, 4.2, 3.3 |
| 7.2 | Build Scheduling Queue Service | Complete | 7.1, 5.1, 2.6 |
| 7.3 | Build Scheduling API Endpoints | Complete | 7.2 |
| 7.4 | Build Calendar Manager | Not Started | 3.3, 2.6 |
| 7.5 | Build Acceptance/Decline Email Agent | Not Started | None |
| 7.6 | Scheduling Flow Tests | Not Started | 7.1–7.5 |

## Acceptance Criteria
- Planning agent suggests feasible work blocks
- Scheduling queue manages approval workflow
- API endpoints support accept, decline, and modify
- Calendar manager creates Outlook events after approval
- Acceptance/decline emails are generated from templates
