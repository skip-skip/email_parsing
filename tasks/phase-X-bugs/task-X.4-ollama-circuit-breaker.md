# Task X.4 — Fix: Monitor Retries Dead Ollama on Every Poll Cycle

## Description
When Ollama is unreachable, every poll cycle (every 30s) attempts classification and times out, wasting resources and filling logs with repeated timeout errors. Add a circuit breaker so the monitor skips classification for a cooldown period after consecutive failures.

## Status
Complete

## Root Cause
- `_poll_async()` runs every 30s and processes all new emails through the classifier
- If Ollama is down, each email triggers 3 timeout retries (~45s with Task X.3 fix)
- Next poll cycle repeats the same failures immediately
- Logs are flooded with "Ollama request attempt X/3 failed" messages

## Subtasks
- Add circuit breaker state to `OutlookMonitor` (or `EmailProcessor`):
  - Track consecutive classification failures and timestamp of last failure
  - After N consecutive failures (e.g., 3), skip classification for a cooldown period (e.g., 5 minutes)
  - Reset the counter on a successful classification
- Log circuit breaker state transitions (opened/closed) at INFO level
- Add unit tests for circuit breaker behavior:
  - Opens after N consecutive failures
  - Skips classification during cooldown
  - Closes after cooldown expires and classification succeeds
  - Resets on successful classification

## Dependencies
- Task X.2, X.3 (should be done after the core timeout fix)

## Acceptance Criteria
- Monitor skips classification after repeated Ollama failures instead of retrying every poll
- Circuit breaker opens after configurable number of consecutive failures (default: 3)
- Circuit breaker cooldown is configurable (default: 5 minutes)
- Successful classification resets the circuit breaker
- Circuit breaker state transitions are logged
- All existing tests pass
