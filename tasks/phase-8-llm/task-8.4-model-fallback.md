# Task 8.4 — Model Fallback Chain

## Description
Implement model fallback for reliability.

## Status
Complete

## Subtasks
- Create `backend/app/services/llm/model_manager.py`:
  - Define fallback chain (qwen3:8b → llama3.3:8b → gemma3:12b)
  - `generate_with_fallback(prompt, system_prompt) -> (str, str)`
  - Track which model was used for each request
  - Log model switches for monitoring
- Add health check for Ollama:
  - `GET /api/llm/health`
  - Periodic check (every 5 minutes)

## Dependencies
- Task 4.1

## Acceptance Criteria
- Falls back to next model on failure
- Tracks which model was used
- Logs model switches
- Health check shows available models
