from __future__ import annotations

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

from backend.app.workflows.graph import compile_workflow, build_workflow_graph


class TestWorkflowGraph:
    def test_graph_compiles(self) -> None:
        wf = compile_workflow()
        assert wf is not None

    def test_build_workflow_graph_returns_state_graph(self) -> None:
        graph = build_workflow_graph()
        assert graph is not None

    @patch("backend.app.agents.email_parsing_agent.EmailParsingAgent")
    def test_complete_ticket_follows_scheduling_path(
        self, mock_agent_cls: MagicMock
    ) -> None:
        mock_agent = MagicMock()
        mock_parsed = MagicMock()
        mock_parsed.client = "Acme Corp"
        mock_parsed.sender = "bob@example.com"
        mock_parsed.subject = "Test"
        mock_parsed.project_number = "PRJ-001"
        mock_parsed.task_description = "Redesign the company website with new branding and features"
        mock_parsed.deadline = datetime(2025, 12, 31, 0, 0, 0)
        mock_parsed.budget_hours = 40.0
        mock_parsed.attachments = []
        mock_parsed.confidence = 0.9
        mock_agent.parse = AsyncMock(return_value=mock_parsed)
        mock_agent_cls.return_value = mock_agent

        wf = compile_workflow()
        result = wf.invoke({
            "ticket_id": "test-ticket-1",
            "status": "",
            "parsed_data": None,
            "validation_result": None,
            "missing_fields": [],
            "error": None,
            "sender": "bob@example.com",
            "subject": "Test Subject",
            "body": "Please redesign the company website with new branding and features by end of month.",
        })

        assert result["status"] == "IN_PROGRESS"

    @patch("backend.app.agents.email_parsing_agent.EmailParsingAgent")
    def test_incomplete_ticket_follows_missing_info_path(
        self, mock_agent_cls: MagicMock
    ) -> None:
        mock_agent = MagicMock()
        mock_parsed = MagicMock()
        mock_parsed.client = None
        mock_parsed.sender = "bob@example.com"
        mock_parsed.subject = "Test"
        mock_parsed.project_number = None
        mock_parsed.task_description = None
        mock_parsed.deadline = None
        mock_parsed.budget_hours = None
        mock_parsed.attachments = []
        mock_parsed.confidence = 0.2
        mock_agent.parse = AsyncMock(return_value=mock_parsed)
        mock_agent_cls.return_value = mock_agent

        wf = compile_workflow()
        result = wf.invoke({
            "ticket_id": "test-ticket-2",
            "status": "",
            "parsed_data": None,
            "validation_result": None,
            "missing_fields": [],
            "error": None,
            "sender": "bob@example.com",
            "subject": "Quick question",
            "body": "Hey, can you help?",
        })

        assert result["status"] == "WAITING_FOR_INFORMATION"
