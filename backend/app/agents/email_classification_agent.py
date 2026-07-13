from __future__ import annotations

import asyncio
import logging
import time
from dataclasses import dataclass

from backend.app.prompts.email_classification import (
    EMAIL_CLASSIFICATION_SYSTEM,
    EMAIL_CLASSIFICATION_USER,
    EMAIL_CLASSIFICATION_VERSION,
)
from backend.app.services.database import async_session_factory
from backend.app.services.database.repositories.ai_log_repository import AILogRepository
from backend.app.services.llm.ollama_client import OllamaClient

logger = logging.getLogger(__name__)

CLASSIFICATION_TIMEOUT = 15


@dataclass
class ClassificationResult:
    """Result of email classification."""

    is_task: bool
    category: str
    confidence: float
    reason: str


class EmailClassificationAgent:
    """Classifies emails as task requests or non-task emails using an LLM.

    Determines whether an email requires action (task_request) or is
    informational, a newsletter, notification, spam, or other non-task
    email. Logs all classifications to the AI audit trail.
    """

    def __init__(self, ollama_client: OllamaClient | None = None) -> None:
        self._client = ollama_client or OllamaClient(timeout=CLASSIFICATION_TIMEOUT)

    async def classify(
        self,
        sender: str,
        subject: str,
        body: str,
        ticket_id: str | None = None,
    ) -> ClassificationResult:
        """Classify an email as a task request or non-task email.

        Args:
            sender: Email sender address.
            subject: Email subject line.
            body: Email body text.
            ticket_id: Optional ticket ID for logging purposes.

        Returns:
            ClassificationResult with is_task, category, confidence, and reason.
            Returns is_task=True on failure (fail-open).
        """
        user_prompt = EMAIL_CLASSIFICATION_USER.format(
            sender=sender,
            subject=subject,
            body=body,
        )

        start_time = time.monotonic()
        try:
            raw_response = await asyncio.to_thread(
                self._client.generate,
                prompt=user_prompt,
                system_prompt=EMAIL_CLASSIFICATION_SYSTEM,
            )
            execution_ms = int((time.monotonic() - start_time) * 1000)

            parsed = self._client._parse_json(raw_response)
            if parsed is None:
                logger.warning("Failed to parse JSON from classification response")
                return self._fail_open_result(sender, subject)

            result = self._build_classification(parsed)

            await self._log_classification(
                raw_response=raw_response,
                parsed_data=parsed,
                confidence=result.confidence,
                execution_ms=execution_ms,
                ticket_id=ticket_id,
            )

            return result

        except Exception:
            execution_ms = int((time.monotonic() - start_time) * 1000)
            logger.exception("Email classification failed")
            await self._log_classification(
                raw_response="",
                parsed_data=None,
                confidence=0.0,
                execution_ms=execution_ms,
                ticket_id=ticket_id,
                error=True,
            )
            return self._fail_open_result(sender, subject)

    def _build_classification(self, data: dict) -> ClassificationResult:
        is_task = bool(data.get("is_task", True))
        category = data.get("category", "other")
        confidence = float(data.get("confidence", 0.0))
        confidence = max(0.0, min(1.0, confidence))
        reason = data.get("reason", "")

        valid_categories = {
            "task_request", "informational", "newsletter",
            "notification", "spam", "other",
        }
        if category not in valid_categories:
            category = "other"

        return ClassificationResult(
            is_task=is_task,
            category=category,
            confidence=confidence,
            reason=reason,
        )

    def _fail_open_result(self, sender: str, subject: str) -> ClassificationResult:
        return ClassificationResult(
            is_task=True,
            category="other",
            confidence=0.0,
            reason="Classification failed, defaulting to task (fail-open)",
        )

    async def _log_classification(
        self,
        raw_response: str,
        parsed_data: dict | None,
        confidence: float,
        execution_ms: int,
        ticket_id: str | None = None,
        error: bool = False,
    ) -> None:
        try:
            async with async_session_factory() as session:
                log_repo = AILogRepository(session)
                import uuid

                ticket_uuid = uuid.UUID(ticket_id) if ticket_id else None
                await log_repo.create(
                    model="ollama",
                    prompt_version=EMAIL_CLASSIFICATION_VERSION,
                    prompt=EMAIL_CLASSIFICATION_SYSTEM,
                    response=raw_response,
                    ticket_id=ticket_uuid,
                    parsed_json=parsed_data,
                    confidence=confidence if not error else None,
                    execution_time_ms=execution_ms,
                )
                await session.commit()
        except Exception:
            logger.exception("Failed to log classification to AILog")
