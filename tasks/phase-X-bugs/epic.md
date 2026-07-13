# Epic X — Bug Fixes: Ollama Blocking & Timeout Issues

## Goal
Fix issues where synchronous Ollama HTTP calls block FastAPI's event loop, stalling the API when Ollama is unreachable or slow. Add resilience to the background email classification pipeline.

## Status
Not Started

## Tasks
| Task | Title | Status | Dependencies |
|------|-------|--------|-------------|
| X.1 | Database Reset | Complete | None |
| X.2 | Fix: Sync Ollama Calls Block Event Loop | Not Started | None |
| X.3 | Fix: Ollama Timeout Too Long for Background Classification | Not Started | X.2 |
| X.4 | Fix: Monitor Retries Dead Ollama on Every Poll Cycle | Not Started | X.2, X.3 |

## Architecture
```
OutlookMonitor._poll_async() [runs on FastAPI event loop]
  → EmailProcessor.process_new_email(msg)
    → EmailClassificationAgent.classify()
      → OllamaClient.generate()  ← BLOCKS event loop (httpx sync)
        → httpx.Client.request()  ← 60s timeout × 3 retries
```

**Fix:** Wrap `generate()` in `asyncio.to_thread()` + reduce timeout + add circuit breaker.

## Acceptance Criteria
- Ollama HTTP calls do not block FastAPI's event loop
- API remains responsive while Ollama is unavailable
- Classification fails fast (~45s worst case) instead of ~180s
- Monitor skips classification after repeated failures (circuit breaker)
- All existing tests pass
