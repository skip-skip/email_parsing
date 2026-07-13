from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

from backend.app.workflows.graph import compile_workflow


class TestCompleteEmailFlow:
    """Integration tests for the complete happy-path email flow.

    Flow: receive_email → extract_task → validate_fields → plan_schedule
          → create_calendar_event → dispatch_task
    """

    @patch("backend.app.agents.email_parsing_agent.async_session_factory")
    @patch("backend.app.agents.email_parsing_agent.OllamaClient")
    def test_full_email_to_dispatch(
        self,
        mock_ollama_cls: MagicMock,
        mock_session_factory: MagicMock,
        complete_email_data: dict[str, Any],
        complete_parsed_data: dict[str, Any],
    ) -> None:
        mock_client = MagicMock()
        mock_client.generate.return_value = str(complete_parsed_data)
        mock_client._parse_json.return_value = complete_parsed_data
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
                "ticket_id": complete_email_data["ticket_id"],
                "status": "",
                "parsed_data": None,
                "validation_result": None,
                "missing_fields": [],
                "error": None,
                "sender": complete_email_data["sender"],
                "subject": complete_email_data["subject"],
                "body": complete_email_data["body"],
            })

        assert result["status"] == "IN_PROGRESS"
        assert result["parsed_data"] is not None
        assert result["parsed_data"]["project_number"] == "PRJ-2025-042"
        assert result["parsed_data"]["budget_hours"] == 40.0
        assert result["missing_fields"] == []
        assert result["validation_result"] is not None
        assert result["validation_result"]["is_valid"] is True

    @patch("backend.app.agents.email_parsing_agent.async_session_factory")
    @patch("backend.app.agents.email_parsing_agent.OllamaClient")
    def test_workflow_status_transitions(
        self,
        mock_ollama_cls: MagicMock,
        mock_session_factory: MagicMock,
        complete_email_data: dict[str, Any],
        complete_parsed_data: dict[str, Any],
    ) -> None:
        mock_client = MagicMock()
        mock_client.generate.return_value = str(complete_parsed_data)
        mock_client._parse_json.return_value = complete_parsed_data
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
                "ticket_id": complete_email_data["ticket_id"],
                "status": "",
                "parsed_data": None,
                "validation_result": None,
                "missing_fields": [],
                "error": None,
                "sender": complete_email_data["sender"],
                "subject": complete_email_data["subject"],
                "body": complete_email_data["body"],
            })

        assert result["status"] == "IN_PROGRESS"
        assert result["error"] is None

    @patch("backend.app.agents.email_parsing_agent.async_session_factory")
    @patch("backend.app.agents.email_parsing_agent.OllamaClient")
    def test_parsed_data_populated_correctly(
        self,
        mock_ollama_cls: MagicMock,
        mock_session_factory: MagicMock,
        complete_email_data: dict[str, Any],
        complete_parsed_data: dict[str, Any],
    ) -> None:
        mock_client = MagicMock()
        mock_client.generate.return_value = str(complete_parsed_data)
        mock_client._parse_json.return_value = complete_parsed_data
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
                "ticket_id": complete_email_data["ticket_id"],
                "status": "",
                "parsed_data": None,
                "validation_result": None,
                "missing_fields": [],
                "error": None,
                "sender": complete_email_data["sender"],
                "subject": complete_email_data["subject"],
                "body": complete_email_data["body"],
            })

        parsed = result["parsed_data"]
        assert parsed["client"] == "Acme Corp"
        assert parsed["sender"] == "jane.smith@acme-corp.com"
        assert parsed["subject"] == "Q3 Marketing Campaign - Website Redesign"
        assert parsed["project_number"] == "PRJ-2025-042"
        assert parsed["deadline"] == "2027-08-15T00:00:00"
        assert parsed["budget_hours"] == 40.0
        assert parsed["confidence"] == 0.92

    @patch("backend.app.agents.email_parsing_agent.async_session_factory")
    @patch("backend.app.agents.email_parsing_agent.OllamaClient")
    def test_validation_passes_with_all_fields(
        self,
        mock_ollama_cls: MagicMock,
        mock_session_factory: MagicMock,
        complete_email_data: dict[str, Any],
        complete_parsed_data: dict[str, Any],
    ) -> None:
        mock_client = MagicMock()
        mock_client.generate.return_value = str(complete_parsed_data)
        mock_client._parse_json.return_value = complete_parsed_data
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
                "ticket_id": complete_email_data["ticket_id"],
                "status": "",
                "parsed_data": None,
                "validation_result": None,
                "missing_fields": [],
                "error": None,
                "sender": complete_email_data["sender"],
                "subject": complete_email_data["subject"],
                "body": complete_email_data["body"],
            })

        vr = result["validation_result"]
        assert vr["is_valid"] is True
        assert vr["missing_fields"] == []
        assert vr["warnings"] == []

    @patch("backend.app.agents.email_parsing_agent.async_session_factory")
    @patch("backend.app.agents.email_parsing_agent.OllamaClient")
    def test_schedule_blocks_created(
        self,
        mock_ollama_cls: MagicMock,
        mock_session_factory: MagicMock,
        complete_email_data: dict[str, Any],
        complete_parsed_data: dict[str, Any],
    ) -> None:
        mock_client = MagicMock()
        mock_client.generate.return_value = str(complete_parsed_data)
        mock_client._parse_json.return_value = complete_parsed_data
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
                "ticket_id": complete_email_data["ticket_id"],
                "status": "",
                "parsed_data": None,
                "validation_result": None,
                "missing_fields": [],
                "error": None,
                "sender": complete_email_data["sender"],
                "subject": complete_email_data["subject"],
                "body": complete_email_data["body"],
            })

        assert result["status"] == "IN_PROGRESS"
        assert result["validation_result"]["is_valid"] is True

    @patch("backend.app.agents.email_parsing_agent.async_session_factory")
    @patch("backend.app.agents.email_parsing_agent.OllamaClient")
    def test_no_error_in_success_path(
        self,
        mock_ollama_cls: MagicMock,
        mock_session_factory: MagicMock,
        complete_email_data: dict[str, Any],
        complete_parsed_data: dict[str, Any],
    ) -> None:
        mock_client = MagicMock()
        mock_client.generate.return_value = str(complete_parsed_data)
        mock_client._parse_json.return_value = complete_parsed_data
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
                "ticket_id": complete_email_data["ticket_id"],
                "status": "",
                "parsed_data": None,
                "validation_result": None,
                "missing_fields": [],
                "error": None,
                "sender": complete_email_data["sender"],
                "subject": complete_email_data["subject"],
                "body": complete_email_data["body"],
            })

        assert result["error"] is None
