# Task 7.1 — Build Calendar Planning Agent

## Description
Create the agent that suggests work blocks based on calendar availability and deadlines.

## Status
Not Started

## Subtasks
- Create `backend/app/agents/calendar_planning_agent.py`:
  - Accept ticket data (deadline, budget_hours) and calendar availability
  - Call `schedule_suggestion` prompt via Ollama client
  - Parse response into `ScheduleSuggestion`:
    - `blocks: list[ScheduleBlock]`
    - `total_hours: float`
    - `fits_deadline: bool`
    - `confidence: float`
  - Validate suggestions:
    - Total hours match budget_hours (±10%)
    - All blocks are before deadline
    - No conflicts with existing calendar events
    - Blocks are during working hours (9am–5pm)
  - Log to AILog table

## Dependencies
- Task 4.1
- Task 4.2
- Task 3.3

## Acceptance Criteria
- Suggests realistic work blocks
- Respects calendar availability
- Total hours match budget
- All blocks before deadline
- Suggestions are logged
