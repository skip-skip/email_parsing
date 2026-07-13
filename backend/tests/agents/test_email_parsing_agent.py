from __future__ import annotations

import asyncio
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

from backend.app.agents.email_parsing_agent import LOW_CONFIDENCE, EmailParsingAgent
from shared.schemas.email import ParsedEmail


class TestEmailParsingAgent:
    """Tests for EmailParsingAgent with mocked LLM and database."""

    SENDER = "bob@example.com"
    SUBJECT = "Website redesign"
    BODY = "Please redesign the company website by end of month."
    RECEIVED_TIME = datetime(2025, 6, 15, 10, 0, 0)

    @patch("backend.app.agents.email_parsing_agent.async_session_factory")
    @patch("backend.app.agents.email_parsing_agent.OllamaClient")
    def test_successful_extraction(
        self, mock_ollama_cls: MagicMock, mock_session_factory: MagicMock
    ) -> None:
        """A valid JSON response from the LLM should produce a populated ParsedEmail."""
        mock_client = MagicMock()
        mock_client.generate.return_value = """{
            "client": "Acme Corp",
            "sender": "bob@example.com",
            "subject": "Website redesign",
            "project_number": "PRJ-2025-001",
            "task_description": "Redesign the company website",
            "deadline": "2025-07-01T00:00:00",
            "budget_hours": 40,
            "attachments": [],
            "confidence": 0.85
        }"""
        mock_client._parse_json.return_value = {
            "client": "Acme Corp",
            "sender": "bob@example.com",
            "subject": "Website redesign",
            "project_number": "PRJ-2025-001",
            "task_description": "Redesign the company website",
            "deadline": "2025-07-01T00:00:00",
            "budget_hours": 40,
            "attachments": [],
            "confidence": 0.85,
        }
        mock_ollama_cls.return_value = mock_client

        mock_session = AsyncMock()
        mock_session_factory.return_value.__aenter__.return_value = mock_session

        with patch(
            "backend.app.agents.email_parsing_agent.AILogRepository",
            return_value=MagicMock(),
        ):
            agent = EmailParsingAgent(ollama_client=mock_client)
            result = asyncio.run(
                agent.parse(
                    sender=self.SENDER,
                    subject=self.SUBJECT,
                    body=self.BODY,
                    received_time=self.RECEIVED_TIME,
                )
            )

        assert isinstance(result, ParsedEmail)
        assert result.client == "Acme Corp"
        assert result.sender == "bob@example.com"
        assert result.subject == "Website redesign"
        assert result.project_number == "PRJ-2025-001"
        assert result.task_description == "Redesign the company website"
        assert result.deadline == datetime(2025, 7, 1, 0, 0, 0)
        assert result.budget_hours == 40.0
        assert result.confidence == 0.85

    @patch("backend.app.agents.email_parsing_agent.async_session_factory")
    @patch("backend.app.agents.email_parsing_agent.OllamaClient")
    def test_json_parse_failure(
        self, mock_ollama_cls: MagicMock, mock_session_factory: MagicMock
    ) -> None:
        """When the LLM returns non-JSON, a low-confidence result should be returned."""
        mock_client = MagicMock()
        mock_client.generate.return_value = "I'm sorry, I cannot parse this email."
        mock_client._parse_json.return_value = None
        mock_ollama_cls.return_value = mock_client

        mock_session = AsyncMock()
        mock_session_factory.return_value.__aenter__.return_value = mock_session

        with patch(
            "backend.app.agents.email_parsing_agent.AILogRepository",
            return_value=MagicMock(),
        ):
            agent = EmailParsingAgent(ollama_client=mock_client)
            result = asyncio.run(
                agent.parse(
                    sender=self.SENDER,
                    subject=self.SUBJECT,
                    body=self.BODY,
                    received_time=self.RECEIVED_TIME,
                )
            )

        assert isinstance(result, ParsedEmail)
        assert result.client is None
        assert result.sender == self.SENDER
        assert result.subject == self.SUBJECT
        assert result.project_number is None
        assert result.task_description is None
        assert result.deadline is None
        assert result.budget_hours is None
        assert result.confidence == LOW_CONFIDENCE

    @patch("backend.app.agents.email_parsing_agent.OllamaClient")
    def test_confidence_calculation(self, mock_ollama_cls: MagicMock) -> None:
        """Confidence values should be clamped between 0.0 and 1.0."""
        test_cases = [
            (1.5, 1.0),
            (-0.5, 0.0),
            (0.0, 0.0),
            (1.0, 1.0),
            (0.75, 0.75),
        ]

        for raw_confidence, expected in test_cases:
            mock_client = MagicMock()
            mock_client.generate.return_value = "{}"
            mock_client._parse_json.return_value = {
                "client": None,
                "sender": self.SENDER,
                "subject": self.SUBJECT,
                "project_number": None,
                "task_description": None,
                "deadline": None,
                "budget_hours": None,
                "attachments": [],
                "confidence": raw_confidence,
            }
            mock_ollama_cls.return_value = mock_client

            agent = EmailParsingAgent(ollama_client=mock_client)
            result = agent._build_parsed_email(
                {
                    "client": None,
                    "sender": self.SENDER,
                    "subject": self.SUBJECT,
                    "project_number": None,
                    "task_description": None,
                    "deadline": None,
                    "budget_hours": None,
                    "attachments": [],
                    "confidence": raw_confidence,
                },
                self.SENDER,
                self.SUBJECT,
            )

            assert result.confidence == expected, (
                f"Expected {expected} for raw confidence {raw_confidence}, "
                f"got {result.confidence}"
            )

    @patch("backend.app.agents.email_parsing_agent.async_session_factory")
    @patch("backend.app.agents.email_parsing_agent.OllamaClient")
    def test_log_extraction_called(
        self, mock_ollama_cls: MagicMock, mock_session_factory: MagicMock
    ) -> None:
        """The AILogRepository.create should be called after a successful parse."""
        mock_client = MagicMock()
        raw_response = '{"client": "Test", "confidence": 0.9}'
        parsed_data = {"client": "Test", "confidence": 0.9}
        mock_client.generate.return_value = raw_response
        mock_client._parse_json.return_value = parsed_data
        mock_ollama_cls.return_value = mock_client

        mock_session = AsyncMock()
        mock_session_factory.return_value.__aenter__.return_value = mock_session

        mock_log_repo = MagicMock()
        mock_log_repo.create = AsyncMock()

        with patch(
            "backend.app.agents.email_parsing_agent.AILogRepository",
            return_value=mock_log_repo,
        ):
            agent = EmailParsingAgent(ollama_client=mock_client)
            asyncio.run(
                agent.parse(
                    sender=self.SENDER,
                    subject=self.SUBJECT,
                    body=self.BODY,
                    received_time=self.RECEIVED_TIME,
                    ticket_id="550e8400-e29b-41d4-a716-446655440000",
                )
            )

        mock_log_repo.create.assert_awaited_once()
        call_kwargs = mock_log_repo.create.await_args[1]
        assert call_kwargs["response"] == raw_response
        assert call_kwargs["parsed_json"] == parsed_data
        assert call_kwargs["confidence"] == 0.9
        assert call_kwargs["execution_time_ms"] is not None

    @patch("backend.app.agents.email_parsing_agent.async_session_factory")
    @patch("backend.app.agents.email_parsing_agent.OllamaClient")
    def test_llm_exception_returns_low_confidence(
        self, mock_ollama_cls: MagicMock, mock_session_factory: MagicMock
    ) -> None:
        """When the LLM raises an exception, a low-confidence result should be returned."""
        mock_client = MagicMock()
        mock_client.generate.side_effect = ConnectionError("Ollama not reachable")
        mock_ollama_cls.return_value = mock_client

        mock_session = AsyncMock()
        mock_session_factory.return_value.__aenter__.return_value = mock_session

        mock_log_repo = MagicMock()
        mock_log_repo.create = AsyncMock()

        with patch(
            "backend.app.agents.email_parsing_agent.AILogRepository",
            return_value=mock_log_repo,
        ):
            agent = EmailParsingAgent(ollama_client=mock_client)
            result = asyncio.run(
                agent.parse(
                    sender=self.SENDER,
                    subject=self.SUBJECT,
                    body=self.BODY,
                    received_time=self.RECEIVED_TIME,
                )
            )

        assert isinstance(result, ParsedEmail)
        assert result.client is None
        assert result.confidence == LOW_CONFIDENCE

        # Verify that the error log was still created
        mock_log_repo.create.assert_awaited_once()
        call_kwargs = mock_log_repo.create.await_args[1]
        assert call_kwargs["confidence"] == LOW_CONFIDENCE
        assert call_kwargs["response"] == ""
        assert call_kwargs["parsed_json"] is None
