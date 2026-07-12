# Epic 5 — Workflow Engine & State Machine

## Goal
Implement the LangGraph-based workflow engine that orchestrates the entire ticket lifecycle through deterministic state transitions.

## Status
Not Started

## Tasks
| Task | Title | Status | Dependencies |
|------|-------|--------|-------------|
| 5.1 | Define Ticket State Machine | Complete | 2.1, 2.6 |
| 5.2 | Set Up LangGraph Workflow | Complete | 5.1 |
| 5.3 | Implement Workflow Nodes | Complete | 4.4, 4.1, 3.2 |
| 5.4 | Implement Validation Engine | Not Started | 1.3 |
| 5.5 | Workflow Integration Tests | Not Started | 5.1–5.4 |

## Acceptance Criteria
- State machine enforces valid transitions
- LangGraph graph compiles and routes correctly
- Each workflow node performs one business function
- Validation engine catches all missing fields
- Full lifecycle completes from NEW to ARCHIVED
