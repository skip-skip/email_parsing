# Task X.2 — Fix: Sync Ollama Calls Block Event Loop

## Description
`EmailClassificationAgent.classify()` calls `OllamaClient.generate()` synchronously from an async method. Since `OllamaClient` uses `httpx.Client` (sync), this blocks FastAPI's asyncio event loop during Ollama HTTP requests. When Ollama is unreachable, each failed classification blocks the event loop for ~180s (60s timeout × 3 retries + backoff sleeps), stalling all API endpoints.

## Status
Complete

## Root Cause
- `EmailClassificationAgent.classify()` (line 67) calls `self._client.generate()` — a sync method
- `OllamaClient.generate()` uses `httpx.Client` (sync) with `OLLAMA_TIMEOUT=60s` per attempt
- `_request_with_retry()` retries 3 times with `time.sleep()` between attempts
- The monitor's `_poll_async()` runs on FastAPI's event loop via `AsyncIOScheduler`
- Blocking the event loop prevents FastAPI from serving any requests

## Subtasks
- Wrap `self._client.generate()` call in `asyncio.to_thread()` inside `EmailClassificationAgent.classify()`
- Update unit tests for `EmailClassificationAgent` to verify the async wrapping works
- Run full test suite to confirm no regressions

## Dependencies
None

## Acceptance Criteria
- Ollama HTTP calls do not block FastAPI's event loop
- API remains responsive while Ollama is timing out or unavailable
- Classification still functions correctly when Ollama is available
- All existing tests pass
