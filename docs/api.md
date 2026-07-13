# API Reference

REST API documentation for the AI Task Manager backend.

**Base URL:** `http://127.0.0.1:8000`

**Content-Type:** `application/json` for all request and response bodies.

## Error Responses

All errors return a consistent format:

```json
{
  "error": {
    "code": 404,
    "message": "Ticket not found"
  }
}
```

| Status Code | Meaning |
|-------------|---------|
| 400 | Bad request |
| 404 | Resource not found |
| 409 | Conflict (resource already processed) |
| 422 | Request validation failed |
| 500 | Internal server error |
| 502 | External service error |

Every response includes an `X-Request-ID` header for traceability.

---

## Health Check

### `GET /health`

Application health check.

**Response:**

```json
{"status": "ok"}
```

---

## Tickets

### `GET /api/tickets/active`

List active tickets (status is ACCEPTED, CALENDAR_CREATED, or IN_PROGRESS).

**Query Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `status` | string | — | Filter by a single status |
| `client` | string | — | Filter by client name (case-insensitive partial match) |
| `sort_by` | string | `deadline` | Sort field: `deadline`, `created_at`, `priority`, `client` |
| `sort_dir` | string | `asc` | Sort direction: `asc` or `desc` |

**Response:** `200 OK`

```json
[
  {
    "ticket_id": "550e8400-e29b-41d4-a716-446655440000",
    "status": "IN_PROGRESS",
    "client": "Acme Corp",
    "contact": "john@acme.com",
    "project_number": "PRJ-001",
    "task_description": "Update website landing page",
    "deadline": "2026-07-15T17:00:00",
    "budget_hours": 8.0,
    "estimated_hours": 6.0,
    "priority": 1,
    "calendar_event_id": null,
    "conversation_id": "AAMkAGI2...",
    "created_at": "2026-07-10T09:00:00",
    "updated_at": "2026-07-11T14:30:00",
    "calendar_events": [
      {
        "calendar_event_id": "evt-001",
        "outlook_event_id": "00000000-0000-0000-0000-000000000001",
        "start_time": "2026-07-14T09:00:00",
        "end_time": "2026-07-14T12:00:00",
        "duration": 3.0,
        "status": "SCHEDULED"
      }
    ]
  }
]
```

### `GET /api/tickets/{ticket_id}`

Get a single ticket by ID with its calendar events.

**Path Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `ticket_id` | UUID | Ticket identifier |

**Response:** `200 OK` — Same shape as individual ticket in the list above.

**Error Response:** `404 Not Found` — Ticket not found.

---

## Missing Information Queue

### `GET /api/queues/missing-info`

List all items in the missing information queue.

**Response:** `200 OK`

```json
[
  {
    "ticket_id": "550e8400-e29b-41d4-a716-446655440000",
    "draft_email": {
      "to": "sender@example.com",
      "subject": "Re: Project Request",
      "body": "Dear Sender,\n\nThank you for your email...",
      "missing_fields": ["project_number", "deadline"],
      "ticket_id": "550e8400-e29b-41d4-a716-446655440000"
    },
    "missing_fields": ["project_number", "deadline"],
    "created_at": "2026-07-10T10:00:00",
    "status": "PENDING",
    "confidence": 0.85,
    "confidence_indicator": {
      "level": "medium",
      "color": "#f59e0b",
      "label": "Medium Confidence"
    }
  }
]
```

### `GET /api/queues/missing-info/{ticket_id}`

Get a single missing info queue item.

**Path Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `ticket_id` | string (UUID) | Ticket identifier |

**Response:** `200 OK` — Single queue item.

**Error Response:** `404 Not Found`

### `POST /api/queues/missing-info/{ticket_id}/approve`

Approve a missing info item. Optionally include edits to the draft email. Triggers the email to be sent via Outlook.

**Path Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `ticket_id` | string (UUID) | Ticket identifier |

**Request Body (optional):**

```json
{
  "edits": {
    "to": "sender@example.com",
    "subject": "Re: Project Request",
    "body": "Edited email body...",
    "missing_fields": ["project_number", "deadline"]
  }
}
```

**Response:** `200 OK` — Updated queue item.

**Error Responses:**
- `404 Not Found` — Queue item not found
- `409 Conflict` — Item already processed

### `POST /api/queues/missing-info/{ticket_id}/reject`

Reject a missing info item.

**Path Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `ticket_id` | string (UUID) | Ticket identifier |

**Request Body (optional):**

```json
{
  "reason": "Not a valid request"
}
```

**Response:** `200 OK` — Updated queue item with status `REJECTED`.

**Error Responses:**
- `404 Not Found` — Queue item not found
- `409 Conflict` — Item already processed

### `PUT /api/queues/missing-info/{ticket_id}/draft`

Update the draft email for a missing info item without approving or rejecting.

**Path Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `ticket_id` | string (UUID) | Ticket identifier |

**Request Body:**

```json
{
  "to": "sender@example.com",
  "subject": "Re: Project Request",
  "body": "Updated email body...",
  "missing_fields": ["project_number", "deadline"]
}
```

**Response:** `200 OK` — Updated queue item.

**Error Response:** `404 Not Found`

---

## Scheduling Queue

### `GET /api/scheduling/queue`

List all items in the scheduling queue.

**Response:** `200 OK`

```json
[
  {
    "ticket_id": "550e8400-e29b-41d4-a716-446655440000",
    "suggestion": {
      "blocks": [
        {
          "start_time": "2026-07-14T09:00:00",
          "end_time": "2026-07-14T12:00:00",
          "hours": 3.0,
          "description": "Website landing page update"
        },
        {
          "start_time": "2026-07-15T13:00:00",
          "end_time": "2026-07-15T16:00:00",
          "hours": 3.0,
          "description": "Website landing page update"
        }
      ],
      "total_hours": 6.0,
      "fits_deadline": true,
      "confidence": 0.9
    },
    "status": "PENDING",
    "created_at": "2026-07-11T10:00:00",
    "confidence": 0.9,
    "confidence_indicator": {
      "level": "high",
      "color": "#22c55e",
      "label": "High Confidence"
    }
  }
]
```

### `GET /api/scheduling/queue/{ticket_id}`

Get a single scheduling queue item.

**Path Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `ticket_id` | string (UUID) | Ticket identifier |

**Response:** `200 OK` — Single scheduling item.

**Error Response:** `404 Not Found`

### `POST /api/scheduling/queue/{ticket_id}/approve`

Approve a scheduling suggestion. Optionally include modified blocks. Triggers Outlook calendar event creation.

**Path Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `ticket_id` | string (UUID) | Ticket identifier |

**Request Body (optional):**

```json
{
  "selected_blocks": [
    {
      "start_time": "2026-07-14T09:00:00",
      "end_time": "2026-07-14T12:00:00",
      "hours": 3.0,
      "description": "Website landing page update"
    }
  ]
}
```

**Response:** `200 OK` — Updated scheduling item with status `APPROVED`.

**Error Responses:**
- `404 Not Found` — Scheduling item not found
- `409 Conflict` — Item already processed

### `POST /api/scheduling/queue/{ticket_id}/decline`

Decline a scheduling suggestion.

**Path Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `ticket_id` | string (UUID) | Ticket identifier |

**Request Body (optional):**

```json
{
  "reason": "Schedule does not work"
}
```

**Response:** `200 OK` — Updated scheduling item with status `DECLINED`.

**Error Responses:**
- `404 Not Found` — Scheduling item not found
- `409 Conflict` — Item already processed

### `POST /api/scheduling/queue/{ticket_id}/modify`

Replace the suggested schedule blocks with user-defined blocks.

**Path Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `ticket_id` | string (UUID) | Ticket identifier |

**Request Body:**

```json
{
  "blocks": [
    {
      "start_time": "2026-07-14T14:00:00",
      "end_time": "2026-07-14T17:00:00",
      "hours": 3.0,
      "description": "Modified work block"
    }
  ]
}
```

**Response:** `200 OK` — Updated scheduling item.

**Error Response:** `404 Not Found`

---

## AI Logs

### `GET /api/ai-logs`

List AI interaction logs with pagination and filtering.

**Query Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `offset` | integer | `0` | Pagination offset (>= 0) |
| `limit` | integer | `50` | Page size (1-200) |
| `model` | string | — | Filter by model name |
| `prompt_version` | string | — | Filter by prompt version |
| `success` | boolean | — | Filter by success/failure |
| `date_from` | datetime | — | Start of date range (ISO 8601) |
| `date_to` | datetime | — | End of date range (ISO 8601) |

**Response:** `200 OK`

```json
{
  "items": [
    {
      "log_id": "log-001",
      "ticket_id": "550e8400-e29b-41d4-a716-446655440000",
      "model": "qwen3:8b",
      "prompt_version": "email-extraction-v1",
      "prompt": "You are an email parsing assistant...",
      "response": "{\"client\": \"Acme Corp\", ...}",
      "parsed_json": {"client": "Acme Corp", "project_number": "PRJ-001"},
      "confidence": 0.85,
      "input_tokens": 256,
      "output_tokens": 128,
      "success": true,
      "error_message": null,
      "execution_time_ms": 1523,
      "created_at": "2026-07-10T10:00:00"
    }
  ],
  "total": 42,
  "offset": 0,
  "limit": 50
}
```

### `GET /api/ai-logs/stats`

Get aggregate statistics for AI interactions.

**Response:** `200 OK`

```json
{
  "total_interactions": 150,
  "successful_interactions": 142,
  "failed_interactions": 8,
  "success_rate": 0.947,
  "avg_execution_time_ms": 1850.5,
  "avg_confidence": 0.82,
  "total_input_tokens": 38400,
  "total_output_tokens": 19200,
  "model_counts": {
    "qwen3:8b": 120,
    "gemma3:12b": 30
  }
}
```

### `GET /api/ai-logs/{ticket_id}`

Get all AI logs for a specific ticket.

**Path Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `ticket_id` | UUID | Ticket identifier |

**Response:** `200 OK` — Array of AI log entries.

---

## LLM Health

### `GET /api/llm/health`

Check health status of configured LLM models and usage statistics.

**Response:** `200 OK`

```json
{
  "status": "healthy",
  "models": {
    "qwen3:8b": {
      "available": true,
      "last_checked": "2026-07-12T10:00:00",
      "last_error": null
    },
    "gemma3:12b": {
      "available": false,
      "last_checked": "2026-07-12T10:00:00",
      "last_error": "Model not found in Ollama"
    }
  },
  "fallback_chain": ["qwen3:8b", "gemma3:12b", "llama3.3:8b"],
  "usage_stats": {
    "total_requests": 150,
    "successful_requests": 142,
    "failed_requests": 8,
    "model_counts": {
      "qwen3:8b": 120,
      "gemma3:12b": 22
    },
    "model_switches": [
      {
        "from_model": "qwen3:8b",
        "to_model": "gemma3:12b",
        "reason": "Connection error",
        "timestamp": "2026-07-11T15:30:00"
      }
    ]
  }
}
```

**Status values:**
- `healthy` — At least one model is available
- `degraded` — No models are available

---

## Application Logs

### `GET /api/logs/app`

List application log entries with pagination and filtering.

**Query Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `offset` | integer | `0` | Pagination offset (>= 0) |
| `limit` | integer | `100` | Page size (1-500) |
| `level` | string | — | Filter by log level (DEBUG, INFO, WARNING, ERROR, CRITICAL) |
| `search` | string | — | Search in log messages (case-insensitive) |
| `request_id` | string | — | Filter by request ID |
| `date_from` | datetime | — | Start of date range |
| `date_to` | datetime | — | End of date range |

**Response:** `200 OK`

```json
{
  "items": [
    {
      "timestamp": "2026-07-12T10:30:00.123",
      "level": "INFO",
      "message": "Application startup complete",
      "module": "backend.app.main",
      "function": "lifespan",
      "line": 44,
      "request_id": "startup"
    }
  ],
  "total": 500,
  "offset": 0,
  "limit": 100
}
```

### `GET /api/logs/requests`

List HTTP request log entries. Same parameters and response shape as `/api/logs/app`, but filtered to request-level logs only.

### `GET /api/logs/stats`

Get log statistics by level.

**Response:** `200 OK`

```json
{
  "total_entries": 1250,
  "entries_by_level": {
    "INFO": 980,
    "WARNING": 200,
    "ERROR": 50,
    "DEBUG": 20
  }
}
```
