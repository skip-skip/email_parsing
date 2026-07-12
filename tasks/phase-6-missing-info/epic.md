# Epic 6 — Missing Information Flow

## Goal
Implement the complete flow for handling tickets with missing information: drafting replies, queuing for user approval, and sending approved responses.

## Status
Not Started

## Tasks
| Task | Title | Status | Dependencies |
|------|-------|--------|-------------|
| 6.1 | Build Email Draft Agent | Complete | 4.1, 4.2 |
| 6.2 | Build Missing Information Queue Service | Complete | 5.1, 6.1, 2.6 |
| 6.3 | Build Missing Info API Endpoints | Not Started | 6.2 |
| 6.4 | Conversation Reply Handling | Not Started | 4.5, 5.4, 6.2 |
| 6.5 | Missing Information Flow Tests | Not Started | 6.1–6.4 |

## Acceptance Criteria
- Draft agent generates professional emails listing missing fields
- Queue service manages pending items with full context
- API endpoints support approve, reject, and draft editing
- Replies merge information and progress tickets
