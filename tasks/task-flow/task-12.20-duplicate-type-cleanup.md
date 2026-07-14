# Task 12.20 — Duplicate Type Cleanup

## Description
The codebase has duplicate type definitions for `EmailMessage`, `TicketStatus`, and `CalendarEvent` across different modules. This creates maintenance risk and potential type mismatches. Consolidate each type to a single source of truth and fix type safety issues.

## Status
Not Started

## Subtasks

### EmailMessage Consolidation
- Current locations:
  - `backend/app/services/outlook/models.py` — dataclass with `email_id: str | None = None`
  - `shared/schemas/email.py` — Pydantic BaseModel with `email_id: UUID`
- Decision: Use the Pydantic model from `shared/schemas/email.py` as the canonical type
- Update `backend/app/services/outlook/models.py`:
  - Remove the `EmailMessage` dataclass
  - Import from `shared.schemas.email` instead
  - Update all references in `outlook/` module to use the shared type
- Update `ConversationHandler` and `ConversationTracker` to use the same type (they already import from shared)

### TicketStatus Consolidation
- Current locations:
  - `backend/app/workflows/states.py` — `TicketStatus(StrEnum)`
  - `shared/schemas/ticket.py` — `TicketStatus(StrEnum)` (identical copy)
- Decision: Use the workflow states module as canonical (it's used by the state machine)
- Update `shared/schemas/ticket.py`:
  - Import `TicketStatus` from `backend.app.workflows.states` (or move to a shared location)
  - Remove the duplicate definition
- Ensure all imports point to the same source

### CalendarEvent Consolidation
- Current locations:
  - `backend/app/models/calendar_event.py` — SQLAlchemy model
  - `shared/schemas/calendar.py` — Pydantic model
  - `backend/app/services/scheduler/calendar_manager.py` — local dataclass
- Decision: Use SQLAlchemy model for DB operations, Pydantic model for API serialization
- Remove the local dataclass from `calendar_manager.py`
- Import the appropriate type based on context

### Type Safety Fixes
- Update `confidence_indicator` type in `api.ts`:
  - Change from `Record<string, string>` to `{ level: string; label: string }`
  - Update `MissingInfoCard.tsx` and `ScheduleCard.tsx` to use the correct type
- Remove vestigial `calendar_event_id` singular field:
  - Remove from `Ticket` and `ActiveTicket` types in `api.ts`
  - Remove from backend `TicketResponse` model if present
  - The `calendar_events` array is the correct field to use

### Write Tests
- Verify all imports resolve correctly
- Verify no circular imports
- Verify type checking passes with mypy/pyright

## Dependencies
None

## Acceptance Criteria
- Each type has a single canonical definition
- No duplicate type definitions across modules
- `confidence_indicator` is properly typed as `{ level: string; label: string }`
- Vestigial `calendar_event_id` field is removed
- All imports resolve to the correct types
- All existing tests pass
- Type checking passes (mypy/pyright)
