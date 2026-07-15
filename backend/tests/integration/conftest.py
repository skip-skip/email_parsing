from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest

# ---------------------------------------------------------------------------
# Realistic email fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def complete_email_data() -> dict[str, Any]:
    return {
        "ticket_id": "550e8400-e29b-41d4-a716-446655440001",
        "sender": "jane.smith@acme-corp.com",
        "subject": "Q3 Marketing Campaign - Website Redesign",
        "body": (
            "Hi team,\n\n"
            "We need to redesign the Acme Corp website for the Q3 marketing campaign. "
            "The project number is PRJ-2025-042. We need this completed by "
            "August 15, 2025. Budget is 40 hours.\n\n"
            "Key requirements:\n"
            "- Updated branding and color scheme\n"
            "- Mobile-responsive design\n"
            "- New landing pages for the campaign\n\n"
            "Please let me know if you have questions.\n\n"
            "Best,\nJane"
        ),
    }


@pytest.fixture
def complete_parsed_data() -> dict[str, Any]:
    return {
        "client": "Acme Corp",
        "sender": "jane.smith@acme-corp.com",
        "subject": "Q3 Marketing Campaign - Website Redesign",
        "project_number": "PRJ-2025-042",
        "task_description": (
            "Redesign the Acme Corp website for Q3 marketing campaign "
            "with updated branding, mobile-responsive design, and new landing pages"
        ),
        "deadline": "2027-08-15T00:00:00",
        "budget_hours": 40.0,
        "attachments": [],
        "confidence": 0.92,
    }


@pytest.fixture
def incomplete_email_data() -> dict[str, Any]:
    return {
        "ticket_id": "550e8400-e29b-41d4-a716-446655440002",
        "sender": "bob.jones@techstart.io",
        "subject": "Help needed with data pipeline",
        "body": (
            "Hey,\n\n"
            "We have a problem with our data pipeline. "
            "Can you take a look and help us fix it?\n\n"
            "Thanks,\nBob"
        ),
    }


@pytest.fixture
def incomplete_parsed_data() -> dict[str, Any]:
    return {
        "client": "TechStart IO",
        "sender": "bob.jones@techstart.io",
        "subject": "Help needed with data pipeline",
        "project_number": None,
        "task_description": None,
        "deadline": None,
        "budget_hours": None,
        "attachments": [],
        "confidence": 0.8,
    }


@pytest.fixture
def reply_email_data() -> dict[str, Any]:
    """Simulates a reply with the previously missing information."""
    return {
        "ticket_id": "550e8400-e29b-41d4-a716-446655440002",
        "sender": "bob.jones@techstart.io",
        "subject": "Re: Help needed with data pipeline",
        "body": (
            "Hi,\n\n"
            "Sorry for the incomplete info. Here are the details:\n"
            "- Project number: PRJ-2025-099\n"
            "- Task: Fix data pipeline ETL process, currently failing on large datasets\n"
            "- Deadline: September 30, 2025\n"
            "- Budget: 20 hours\n\n"
            "Thanks,\nBob"
        ),
    }


@pytest.fixture
def reply_parsed_data() -> dict[str, Any]:
    """Parsed data from the reply email with complete information."""
    return {
        "client": "TechStart IO",
        "sender": "bob.jones@techstart.io",
        "subject": "Re: Help needed with data pipeline",
        "project_number": "PRJ-2025-099",
        "task_description": (
            "Fix data pipeline ETL process, currently failing on large datasets"
        ),
        "deadline": "2025-09-30T00:00:00",
        "budget_hours": 20.0,
        "attachments": [],
        "confidence": 0.88,
    }


# ---------------------------------------------------------------------------
# Mock builders
# ---------------------------------------------------------------------------

def build_ollama_mock(parsed_response: dict[str, Any]) -> MagicMock:
    """Build a mock OllamaClient that returns the given parsed data."""
    mock_client = MagicMock()
    mock_client.generate.return_value = str(parsed_response)
    mock_client._parse_json.return_value = parsed_response
    mock_client._get_client.return_value = MagicMock()
    return mock_client


def build_workflow_initial_state(
    ticket_id: str,
    sender: str,
    subject: str,
    body: str,
) -> dict[str, Any]:
    return {
        "ticket_id": ticket_id,
        "status": "",
        "parsed_data": None,
        "validation_result": None,
        "missing_fields": [],
        "error": None,
        "sender": sender,
        "subject": subject,
        "body": body,
    }


def build_db_session_mock() -> MagicMock:
    """Build a mock async database session for agent logging."""
    mock_session = AsyncMock()
    mock_session_factory = MagicMock()
    mock_session_factory.return_value.__aenter__ = AsyncMock(
        return_value=mock_session
    )
    mock_session_factory.return_value.__aexit__ = AsyncMock(return_value=False)
    return mock_session_factory
