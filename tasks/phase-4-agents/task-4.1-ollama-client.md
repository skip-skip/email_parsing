# Task 4.1 — Set Up Ollama Client Service

## Description
Create a service that wraps Ollama API calls for the rest of the application.

## Status
Complete

## Subtasks
- Create `backend/app/services/llm/` directory
- Create `ollama_client.py`:
  - Initialize with configurable `OLLAMA_BASE_URL` (default `http://localhost:11434`)
  - Implement `generate(model, prompt, system_prompt) -> str`
  - Implement `generate_json(model, prompt, system_prompt) -> dict`
    - Parses JSON from LLM response
    - Handles markdown code fences around JSON
    - Retries once if JSON parsing fails
  - Implement `list_models() -> list[str]`
  - Add configurable timeout (default 60s)
  - Add retry logic (3 attempts with exponential backoff)
- Create `model_config.py`:
  - Default model selection (`OLLAMA_MODEL`, default `qwen3:8b`)
  - Model fallback chain
  - Temperature and parameter defaults

## Dependencies
- Task 1.1

## Acceptance Criteria
- Can connect to local Ollama instance
- Can generate text responses
- Can generate and parse JSON responses
- Handles connection errors gracefully
- Retries on transient failures
