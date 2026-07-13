from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

from backend.app.agents.email_draft_agent import DraftEmail, EmailDraftAgent


class TestEmailDraftAgent:
    @patch("backend.app.agents.email_draft_agent.async_session_factory")
    @patch("backend.app.agents.email_draft_agent.OllamaClient")
    def test_draft_generation(self, mock_ollama_cls: MagicMock, mock_session_factory: MagicMock) -> None:
        mock_client = MagicMock()
        mock_client.generate.return_value = "Dear Bob, Please provide project number and deadline."
        mock_ollama_cls.return_value = mock_client

        mock_session = AsyncMock()
        mock_session_factory.return_value.__aenter__.return_value = mock_session

        with patch("backend.app.agents.email_draft_agent.AILogRepository", return_value=MagicMock()):
            agent = EmailDraftAgent(ollama_client=mock_client)
            result = asyncio.run(
                agent.draft(
                    ticket_id="550e8400-e29b-41d4-a716-446655440000",
                    sender="bob@example.com",
                    subject="Website redesign",
                    client="Acme Corp",
                    project_number=None,
                    task_description="Redesign website",
                    missing_fields=["project_number", "deadline"],
                )
            )

        assert isinstance(result, DraftEmail)
        assert result.to == "bob@example.com"
        assert result.subject == "Re: Website redesign"
        assert "project_number" in result.missing_fields
        assert "deadline" in result.missing_fields

    @patch("backend.app.agents.email_draft_agent.async_session_factory")
    @patch("backend.app.agents.email_draft_agent.OllamaClient")
    def test_template_fallback(self, mock_ollama_cls: MagicMock, mock_session_factory: MagicMock) -> None:
        mock_client = MagicMock()
        mock_client.generate.side_effect = ConnectionError("Ollama not reachable")
        mock_ollama_cls.return_value = mock_client

        mock_session = AsyncMock()
        mock_session_factory.return_value.__aenter__.return_value = mock_session

        with patch("backend.app.agents.email_draft_agent.AILogRepository", return_value=MagicMock()):
            agent = EmailDraftAgent(ollama_client=mock_client)
            result = asyncio.run(
                agent.draft(
                    ticket_id="550e8400-e29b-41d4-a716-446655440000",
                    sender="bob@example.com",
                    subject="Website redesign",
                    client="Acme Corp",
                    project_number=None,
                    task_description="Redesign website",
                    missing_fields=["project_number", "deadline"],
                )
            )

        assert isinstance(result, DraftEmail)
        assert "project_number" in result.body
        assert "deadline" in result.body
