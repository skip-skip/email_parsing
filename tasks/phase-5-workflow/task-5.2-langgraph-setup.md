# Task 5.2 — Set Up LangGraph Workflow

## Description
Create the LangGraph workflow graph that coordinates all agents.

## Status
Complete

## Subtasks
- Install LangGraph
- Create `backend/app/workflows/graph.py`:
  - Define `WorkflowState` TypedDict
  - Create workflow graph with nodes:
    - `receive_email` → `extract_task` → `validate_fields` → `route_by_validation`
    - `route_by_validation` branches to:
      - `draft_missing_info_email` (if missing fields)
      - `plan_schedule` (if complete)
    - `draft_missing_info_email` → `wait_for_approval`
    - `plan_schedule` → `schedule_approval`
    - `schedule_approval` → `create_calendar_event` → `dispatch_task`
  - Add edges with conditional routing
  - Compile the graph
- Register workflow as a FastAPI service

## Dependencies
- Task 5.1

## Acceptance Criteria
- Graph compiles without errors
- All nodes are connected correctly
- Conditional routing works for missing vs complete tickets
- Graph can be invoked with a `WorkflowState`
