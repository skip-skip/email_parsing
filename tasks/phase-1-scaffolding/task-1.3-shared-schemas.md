# Task 1.3 — Create Shared Schemas

## Description
Define Pydantic models and TypeScript types that both backend and frontend will use.

## Status
Complete

## Subtasks
- Create `shared/schemas/` directory
- Create `ticket.py` with Pydantic models:
  - `TicketCreate`
  - `TicketResponse`
  - `TicketUpdate`
  - `TicketStatus` (enum matching lifecycle)
- Create `email.py` with:
  - `EmailMessage`
  - `ParsedEmail`
- Create `calendar.py` with:
  - `CalendarEvent`
  - `ScheduleBlock`
- Create `ai.py` with:
  - `AIDecision`
  - `ConfidenceScore`
- Create TypeScript type definitions in `shared/types/` mirroring Pydantic models

## Dependencies
- Task 1.1
- Task 1.2

## Acceptance Criteria
- Pydantic models validate correctly with sample data
- TypeScript types compile without errors
- Both sides use identical field names and types
