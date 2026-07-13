from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

from backend.app.workflows.graph import compile_workflow
from backend.app.workflows.nodes.draft_missing_info_email import (
    draft_missing_info_email,
)


class TestMissingInfoFlow:
    """Integration tests for the missing-info workflow path.

    Flow: receive_email → extract_task → validate_fields
          → (missing fields) → draft_missing_info_email → END
    """

    @patch("backend.app.agents.email_parsing_agent.async_session_factory")
    @patch("backend.app.agents.email_parsing_agent.OllamaClient")
    def test_incomplete_email_routes_to_draft(
        self,
        mock_ollama_cls: MagicMock,
        mock_session_factory: MagicMock,
        incomplete_email_data: dict[str, Any],
        incomplete_parsed_data: dict[str, Any],
    ) -> None:
        mock_client = MagicMock()
        mock_client.generate.return_value = str(incomplete_parsed_data)
        mock_client._parse_json.return_value = incomplete_parsed_data
        mock_client._get_client.return_value = MagicMock()
        mock_ollama_cls.return_value = mock_client

        mock_session = AsyncMock()
        mock_session_factory.return_value.__aenter__.return_value = mock_session
        mock_session_factory.return_value.__aexit__ = AsyncMock(return_value=False)

        mock_log_repo = MagicMock()
        mock_log_repo.create = AsyncMock()

        with patch(
            "backend.app.agents.email_parsing_agent.AILogRepository",
            return_value=mock_log_repo,
        ):
            wf = compile_workflow()
            result = wf.invoke({
                "ticket_id": incomplete_email_data["ticket_id"],
                "status": "",
                "parsed_data": None,
                "validation_result": None,
                "missing_fields": [],
                "error": None,
                "sender": incomplete_email_data["sender"],
                "subject": incomplete_email_data["subject"],
                "body": incomplete_email_data["body"],
            })

        assert result["status"] == "WAITING_FOR_INFORMATION"
        assert len(result["missing_fields"]) > 0
        assert result["error"] is None

    @patch("backend.app.agents.email_parsing_agent.async_session_factory")
    @patch("backend.app.agents.email_parsing_agent.OllamaClient")
    def test_missing_fields_detected_correctly(
        self,
        mock_ollama_cls: MagicMock,
        mock_session_factory: MagicMock,
        incomplete_email_data: dict[str, Any],
        incomplete_parsed_data: dict[str, Any],
    ) -> None:
        mock_client = MagicMock()
        mock_client.generate.return_value = str(incomplete_parsed_data)
        mock_client._parse_json.return_value = incomplete_parsed_data
        mock_client._get_client.return_value = MagicMock()
        mock_ollama_cls.return_value = mock_client

        mock_session = AsyncMock()
        mock_session_factory.return_value.__aenter__.return_value = mock_session
        mock_session_factory.return_value.__aexit__ = AsyncMock(return_value=False)

        mock_log_repo = MagicMock()
        mock_log_repo.create = AsyncMock()

        with patch(
            "backend.app.agents.email_parsing_agent.AILogRepository",
            return_value=mock_log_repo,
        ):
            wf = compile_workflow()
            result = wf.invoke({
                "ticket_id": incomplete_email_data["ticket_id"],
                "status": "",
                "parsed_data": None,
                "validation_result": None,
                "missing_fields": [],
                "error": None,
                "sender": incomplete_email_data["sender"],
                "subject": incomplete_email_data["subject"],
                "body": incomplete_email_data["body"],
            })

        missing = result["missing_fields"]
        assert "project_number" in missing
        assert "task_description" in missing
        assert "deadline" in missing
        assert "budget_hours" in missing

    @patch("backend.app.agents.email_parsing_agent.async_session_factory")
    @patch("backend.app.agents.email_parsing_agent.OllamaClient")
    def test_draft_email_generated(
        self,
        mock_ollama_cls: MagicMock,
        mock_session_factory: MagicMock,
        incomplete_email_data: dict[str, Any],
        incomplete_parsed_data: dict[str, Any],
    ) -> None:
        mock_client = MagicMock()
        mock_client.generate.return_value = str(incomplete_parsed_data)
        mock_client._parse_json.return_value = incomplete_parsed_data
        mock_client._get_client.return_value = MagicMock()
        mock_ollama_cls.return_value = mock_client

        mock_session = AsyncMock()
        mock_session_factory.return_value.__aenter__.return_value = mock_session
        mock_session_factory.return_value.__aexit__ = AsyncMock(return_value=False)

        mock_log_repo = MagicMock()
        mock_log_repo.create = AsyncMock()

        with patch(
            "backend.app.agents.email_parsing_agent.AILogRepository",
            return_value=mock_log_repo,
        ):
            wf = compile_workflow()
            result = wf.invoke({
                "ticket_id": incomplete_email_data["ticket_id"],
                "status": "",
                "parsed_data": None,
                "validation_result": None,
                "missing_fields": [],
                "error": None,
                "sender": incomplete_email_data["sender"],
                "subject": incomplete_email_data["subject"],
                "body": incomplete_email_data["body"],
            })

        assert result["status"] == "WAITING_FOR_INFORMATION"

        node_result = draft_missing_info_email(result)
        assert "draft_email" in node_result
        draft = node_result["draft_email"]
        assert isinstance(draft, str)
        assert "project_number" in draft
        assert "deadline" in draft

    @patch("backend.app.agents.email_parsing_agent.async_session_factory")
    @patch("backend.app.agents.email_parsing_agent.OllamaClient")
    def test_workflow_does_not_reach_calendar(
        self,
        mock_ollama_cls: MagicMock,
        mock_session_factory: MagicMock,
        incomplete_email_data: dict[str, Any],
        incomplete_parsed_data: dict[str, Any],
    ) -> None:
        mock_client = MagicMock()
        mock_client.generate.return_value = str(incomplete_parsed_data)
        mock_client._parse_json.return_value = incomplete_parsed_data
        mock_client._get_client.return_value = MagicMock()
        mock_ollama_cls.return_value = mock_client

        mock_session = AsyncMock()
        mock_session_factory.return_value.__aenter__.return_value = mock_session
        mock_session_factory.return_value.__aexit__ = AsyncMock(return_value=False)

        mock_log_repo = MagicMock()
        mock_log_repo.create = AsyncMock()

        with patch(
            "backend.app.agents.email_parsing_agent.AILogRepository",
            return_value=mock_log_repo,
        ):
            wf = compile_workflow()
            result = wf.invoke({
                "ticket_id": incomplete_email_data["ticket_id"],
                "status": "",
                "parsed_data": None,
                "validation_result": None,
                "missing_fields": [],
                "error": None,
                "sender": incomplete_email_data["sender"],
                "subject": incomplete_email_data["subject"],
                "body": incomplete_email_data["body"],
            })

        assert result["status"] == "WAITING_FOR_INFORMATION"
        assert "calendar_event_id" not in result

    @patch("backend.app.agents.email_parsing_agent.async_session_factory")
    @patch("backend.app.agents.email_parsing_agent.OllamaClient")
    def test_validation_result_shows_incomplete(
        self,
        mock_ollama_cls: MagicMock,
        mock_session_factory: MagicMock,
        incomplete_email_data: dict[str, Any],
        incomplete_parsed_data: dict[str, Any],
    ) -> None:
        mock_client = MagicMock()
        mock_client.generate.return_value = str(incomplete_parsed_data)
        mock_client._parse_json.return_value = incomplete_parsed_data
        mock_client._get_client.return_value = MagicMock()
        mock_ollama_cls.return_value = mock_client

        mock_session = AsyncMock()
        mock_session_factory.return_value.__aenter__.return_value = mock_session
        mock_session_factory.return_value.__aexit__ = AsyncMock(return_value=False)

        mock_log_repo = MagicMock()
        mock_log_repo.create = AsyncMock()

        with patch(
            "backend.app.agents.email_parsing_agent.AILogRepository",
            return_value=mock_log_repo,
        ):
            wf = compile_workflow()
            result = wf.invoke({
                "ticket_id": incomplete_email_data["ticket_id"],
                "status": "",
                "parsed_data": None,
                "validation_result": None,
                "missing_fields": [],
                "error": None,
                "sender": incomplete_email_data["sender"],
                "subject": incomplete_email_data["subject"],
                "body": incomplete_email_data["body"],
            })

        vr = result["validation_result"]
        assert vr is not None
        assert vr["is_valid"] is False
        assert len(vr["missing_fields"]) >= 3

    @patch("backend.app.agents.email_parsing_agent.async_session_factory")
    @patch("backend.app.agents.email_parsing_agent.OllamaClient")
    def test_partial_completion_with_some_fields(
        self,
        mock_ollama_cls: MagicMock,
        mock_session_factory: MagicMock,
    ) -> None:
        partial_parsed: dict[str, Any] = {
            "client": "Acme Corp",
            "sender": "jane@acme.com",
            "subject": "Fix the server",
            "project_number": "PRJ-001",
            "task_description": "Fix the production server that keeps crashing",
            "deadline": None,
            "budget_hours": None,
            "attachments": [],
            "confidence": 0.5,
        }

        mock_client = MagicMock()
        mock_client.generate.return_value = str(partial_parsed)
        mock_client._parse_json.return_value = partial_parsed
        mock_client._get_client.return_value = MagicMock()
        mock_ollama_cls.return_value = mock_client

        mock_session = AsyncMock()
        mock_session_factory.return_value.__aenter__.return_value = mock_session
        mock_session_factory.return_value.__aexit__ = AsyncMock(return_value=False)

        mock_log_repo = MagicMock()
        mock_log_repo.create = AsyncMock()

        with patch(
            "backend.app.agents.email_parsing_agent.AILogRepository",
            return_value=mock_log_repo,
        ):
            wf = compile_workflow()
            result = wf.invoke({
                "ticket_id": "550e8400-e29b-41d4-a716-446655440003",
                "status": "",
                "parsed_data": None,
                "validation_result": None,
                "missing_fields": [],
                "error": None,
                "sender": "jane@acme.com",
                "subject": "Fix the server",
                "body": "Please fix the production server.",
            })

        assert result["status"] == "WAITING_FOR_INFORMATION"
        missing = result["missing_fields"]
        assert "project_number" not in missing
        assert "task_description" not in missing
        assert "deadline" in missing
        assert "budget_hours" in missing
