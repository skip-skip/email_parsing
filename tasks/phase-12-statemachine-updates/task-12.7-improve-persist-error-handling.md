# Task 12.7 -- Improve _persist_ticket_status Error Handling

## Status
Not Started

## Description
Improve the error handling in _persist_ticket_status to log failures at ERROR level and consider re-raising or returning a failure indicator. Currently, exceptions are caught and logged but the caller has no way to know the status was not persisted.

## Files to Modify
- `backend/app/services/email_processor.py:346-349` -- Improve exception handling

## Implementation Details

### email_processor.py
Change the exception handler from:
```python
except Exception:
    logger.exception(
        "Failed to persist status %s for ticket %s", status, ticket_id
    )
```
To:
```python
except Exception:
    logger.exception(
        "Failed to persist status %s for ticket %s", status, ticket_id
    )
    raise
```

Or alternatively, return a boolean success indicator:
```python
except Exception:
    logger.exception(
        "Failed to persist status %s for ticket %s", status, ticket_id
    )
    return False
return True
```

## Acceptance Criteria
- _persist_ticket_status logs failures at ERROR level (already does via logger.exception)
- _persist_ticket_status either re-raises or returns success indicator
- Callers can detect persistence failures

## Testing
- Verify logger.exception is called on failure
- Verify behavior when transition_ticket raises an exception
- Run existing tests to ensure no regressions
