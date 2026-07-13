from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

from backend.app.agents.email_classification_agent import (
    EmailClassificationAgent,
)


class TestEmailClassificationAgent:
    """Tests for EmailClassificationAgent with mocked LLM and database."""

    SENDER = "bob@example.com"
    SUBJECT = "Website redesign"
    BODY = "Please redesign the company website by end of month."

    @patch("backend.app.agents.email_classification_agent.async_session_factory")
    @patch("backend.app.agents.email_classification_agent.OllamaClient")
    def test_classify_task_request(
        self, mock_ollama_cls: MagicMock, mock_session_factory: MagicMock
    ) -> None:
        """A task request email should be classified as is_task=True."""
        mock_client = MagicMock()
        mock_client.generate.return_value = """{
            "is_task": true,
            "category": "task_request",
            "confidence": 0.95,
            "reason": "Client requesting work with deadline"
        }"""
        mock_client._parse_json.return_value = {
            "is_task": True,
            "category": "task_request",
            "confidence": 0.95,
            "reason": "Client requesting work with deadline",
        }
        mock_ollama_cls.return_value = mock_client

        mock_session = AsyncMock()
        mock_session_factory.return_value.__aenter__.return_value = mock_session

        with patch(
            "backend.app.agents.email_classification_agent.AILogRepository",
            return_value=MagicMock(),
        ):
            agent = EmailClassificationAgent(ollama_client=mock_client)
            result = asyncio.run(
                agent.classify(
                    sender=self.SENDER,
                    subject=self.SUBJECT,
                    body=self.BODY,
                )
            )

        assert result.is_task is True
        assert result.category == "task_request"
        assert result.confidence == 0.95
        assert "deadline" in result.reason.lower()

    @patch("backend.app.agents.email_classification_agent.async_session_factory")
    @patch("backend.app.agents.email_classification_agent.OllamaClient")
    def test_classify_newsletter(
        self, mock_ollama_cls: MagicMock, mock_session_factory: MagicMock
    ) -> None:
        """A newsletter email should be classified as is_task=False."""
        mock_client = MagicMock()
        mock_client.generate.return_value = """{
            "is_task": false,
            "category": "newsletter",
            "confidence": 0.92,
            "reason": "Marketing newsletter from mailing list"
        }"""
        mock_client._parse_json.return_value = {
            "is_task": False,
            "category": "newsletter",
            "confidence": 0.92,
            "reason": "Marketing newsletter from mailing list",
        }
        mock_ollama_cls.return_value = mock_client

        mock_session = AsyncMock()
        mock_session_factory.return_value.__aenter__.return_value = mock_session

        with patch(
            "backend.app.agents.email_classification_agent.AILogRepository",
            return_value=MagicMock(),
        ):
            agent = EmailClassificationAgent(ollama_client=mock_client)
            result = asyncio.run(
                agent.classify(
                    sender="newsletter@company.com",
                    subject="Monthly Update",
                    body="Check out our latest features and products.",
                )
            )

        assert result.is_task is False
        assert result.category == "newsletter"
        assert result.confidence == 0.92

    @patch("backend.app.agents.email_classification_agent.async_session_factory")
    @patch("backend.app.agents.email_classification_agent.OllamaClient")
    def test_classify_notification(
        self, mock_ollama_cls: MagicMock, mock_session_factory: MagicMock
    ) -> None:
        """A system notification should be classified as is_task=False."""
        mock_client = MagicMock()
        mock_client.generate.return_value = """{
            "is_task": false,
            "category": "notification",
            "confidence": 0.88,
            "reason": "Automated system notification"
        }"""
        mock_client._parse_json.return_value = {
            "is_task": False,
            "category": "notification",
            "confidence": 0.88,
            "reason": "Automated system notification",
        }
        mock_ollama_cls.return_value = mock_client

        mock_session = AsyncMock()
        mock_session_factory.return_value.__aenter__.return_value = mock_session

        with patch(
            "backend.app.agents.email_classification_agent.AILogRepository",
            return_value=MagicMock(),
        ):
            agent = EmailClassificationAgent(ollama_client=mock_client)
            result = asyncio.run(
                agent.classify(
                    sender="noreply@system.com",
                    subject="Your report is ready",
                    body="Your weekly report has been generated.",
                )
            )

        assert result.is_task is False
        assert result.category == "notification"
        assert result.confidence == 0.88

    @patch("backend.app.agents.email_classification_agent.async_session_factory")
    @patch("backend.app.agents.email_classification_agent.OllamaClient")
    def test_json_parse_failure_fails_open(
        self, mock_ollama_cls: MagicMock, mock_session_factory: MagicMock
    ) -> None:
        """When JSON parsing fails, should default to is_task=True (fail-open)."""
        mock_client = MagicMock()
        mock_client.generate.return_value = "I cannot classify this email."
        mock_client._parse_json.return_value = None
        mock_ollama_cls.return_value = mock_client

        mock_session = AsyncMock()
        mock_session_factory.return_value.__aenter__.return_value = mock_session

        with patch(
            "backend.app.agents.email_classification_agent.AILogRepository",
            return_value=MagicMock(),
        ):
            agent = EmailClassificationAgent(ollama_client=mock_client)
            result = asyncio.run(
                agent.classify(
                    sender=self.SENDER,
                    subject=self.SUBJECT,
                    body=self.BODY,
                )
            )

        assert result.is_task is True
        assert result.category == "other"
        assert result.confidence == 0.0
        assert "fail-open" in result.reason.lower()

    @patch("backend.app.agents.email_classification_agent.async_session_factory")
    @patch("backend.app.agents.email_classification_agent.OllamaClient")
    def test_llm_exception_fails_open(
        self, mock_ollama_cls: MagicMock, mock_session_factory: MagicMock
    ) -> None:
        """When the LLM raises an exception, should default to is_task=True (fail-open)."""
        mock_client = MagicMock()
        mock_client.generate.side_effect = ConnectionError("Ollama not reachable")
        mock_ollama_cls.return_value = mock_client

        mock_session = AsyncMock()
        mock_session_factory.return_value.__aenter__.return_value = mock_session

        mock_log_repo = MagicMock()
        mock_log_repo.create = AsyncMock()

        with patch(
            "backend.app.agents.email_classification_agent.AILogRepository",
            return_value=mock_log_repo,
        ):
            agent = EmailClassificationAgent(ollama_client=mock_client)
            result = asyncio.run(
                agent.classify(
                    sender=self.SENDER,
                    subject=self.SUBJECT,
                    body=self.BODY,
                )
            )

        assert result.is_task is True
        assert result.category == "other"
        assert result.confidence == 0.0
        assert "fail-open" in result.reason.lower()

        mock_log_repo.create.assert_awaited_once()

    @patch("backend.app.agents.email_classification_agent.async_session_factory")
    @patch("backend.app.agents.email_classification_agent.OllamaClient")
    def test_confidence_clamping(
        self, mock_ollama_cls: MagicMock, mock_session_factory: MagicMock
    ) -> None:
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
                "is_task": True,
                "category": "task_request",
                "confidence": raw_confidence,
                "reason": "test",
            }
            mock_ollama_cls.return_value = mock_client

            agent = EmailClassificationAgent(ollama_client=mock_client)
            result = agent._build_classification(
                {
                    "is_task": True,
                    "category": "task_request",
                    "confidence": raw_confidence,
                    "reason": "test",
                }
            )

            assert result.confidence == expected, (
                f"Expected {expected} for raw confidence {raw_confidence}, "
                f"got {result.confidence}"
            )

    @patch("backend.app.agents.email_classification_agent.async_session_factory")
    @patch("backend.app.agents.email_classification_agent.OllamaClient")
    def test_invalid_category_defaults_to_other(
        self, mock_ollama_cls: MagicMock, mock_session_factory: MagicMock
    ) -> None:
        """Invalid category values should default to 'other'."""
        mock_client = MagicMock()
        mock_client._parse_json.return_value = {
            "is_task": True,
            "category": "invalid_category",
            "confidence": 0.8,
            "reason": "test",
        }
        mock_ollama_cls.return_value = mock_client

        agent = EmailClassificationAgent(ollama_client=mock_client)
        result = agent._build_classification(
            {
                "is_task": True,
                "category": "invalid_category",
                "confidence": 0.8,
                "reason": "test",
            }
        )

        assert result.category == "other"

    @patch("backend.app.agents.email_classification_agent.async_session_factory")
    @patch("backend.app.agents.email_classification_agent.OllamaClient")
    def test_log_classification_called(
        self, mock_ollama_cls: MagicMock, mock_session_factory: MagicMock
    ) -> None:
        """The AILogRepository.create should be called after a successful classification."""
        mock_client = MagicMock()
        raw_response = '{"is_task": true, "category": "task_request", "confidence": 0.9, "reason": "test"}'
        parsed_data = {
            "is_task": True,
            "category": "task_request",
            "confidence": 0.9,
            "reason": "test",
        }
        mock_client.generate.return_value = raw_response
        mock_client._parse_json.return_value = parsed_data
        mock_ollama_cls.return_value = mock_client

        mock_session = AsyncMock()
        mock_session_factory.return_value.__aenter__.return_value = mock_session

        mock_log_repo = MagicMock()
        mock_log_repo.create = AsyncMock()

        with patch(
            "backend.app.agents.email_classification_agent.AILogRepository",
            return_value=mock_log_repo,
        ):
            agent = EmailClassificationAgent(ollama_client=mock_client)
            asyncio.run(
                agent.classify(
                    sender=self.SENDER,
                    subject=self.SUBJECT,
                    body=self.BODY,
                    ticket_id="550e8400-e29b-41d4-a716-446655440000",
                )
            )

        mock_log_repo.create.assert_awaited_once()
        call_kwargs = mock_log_repo.create.await_args[1]
        assert call_kwargs["response"] == raw_response
        assert call_kwargs["parsed_json"] == parsed_data
        assert call_kwargs["confidence"] == 0.9
        assert call_kwargs["execution_time_ms"] is not None
