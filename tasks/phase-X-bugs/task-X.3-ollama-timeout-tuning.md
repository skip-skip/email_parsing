# Task X.3 — Fix: Ollama Timeout Too Long for Background Classification

## Description
The default `OLLAMA_TIMEOUT=60s` × 3 retries means a single failed classification attempt blocks for ~180s. For background email classification in the poll loop, this is excessive. Classification should fail fast so the monitor can continue processing other emails and the next poll cycle can proceed.

## Status
Complete

## Root Cause
- `OllamaClient` defaults to `OLLAMA_TIMEOUT=60s` (env var)
- `EmailClassificationAgent` creates `OllamaClient()` with no timeout override
- 3 retries × 60s + exponential backoff sleeps = ~180s worst case per email
- Multiple new emails compound the blocking time

## Subtasks
- Create the `OllamaClient` used by `EmailClassificationAgent` with a shorter timeout (15s per attempt)
- This can be done in `EmailProcessor.__init__()` or `EmailClassificationAgent.__init__()` by passing `timeout=15` to `OllamaClient()`
- Verify classification still works with shorter timeout when Ollama is responsive
- Update tests if needed

## Dependencies
- Task X.2 (should be done together since both touch the same code path)

## Acceptance Criteria
- Classification timeout is ~15s per attempt (45s worst case for 3 retries) instead of ~180s
- Classification still succeeds when Ollama responds within 15s
- The default `OLLAMA_TIMEOUT=60s` remains unchanged for other Ollama callers (e.g., email parsing, health checks)
- All existing tests pass
