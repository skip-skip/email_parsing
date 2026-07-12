from __future__ import annotations

import logging
import time
from datetime import datetime

from shared.schemas.email import ParsedEmail

from backend.app.prompts.email_extraction import (
    EMAIL_EXTRACTION_SYSTEM,
    EMAIL_EXTRACTION_USER,
    EMAIL_EXTRACTION_VERSION,
)
from backend.app.services.database import async_session_factory
from backend.app.services.database.repositories.ai_log_repository import AILogRepository
from backend.app.services.llm.ollama_client import OllamaClient

logger = logging.getLogger(__name__)

LOW_CONFIDENCE = 0.1


class EmailParsingAgent:
    def __init__(self, ollama_client: OllamaClient | None = None) -> None:
        self._client = ollama_client or OllamaClient()

    async def parse(
        self,
        sender: str,
        subject: str,
        body: str,
        received_time: datetime | None = None,
        ticket_id: str | None = None,
    ) -> ParsedEmail:
        user_prompt = EMAIL_EXTRACTION_USER.format(
            sender=sender,
            subject=subject,
            received_time=received_time.isoformat() if received_time else "unknown",
            body=body,
        )

        start_time = time.monotonic()
        try:
            raw_response = self._client.generate(
                prompt=user_prompt,
                system_prompt=EMAIL_EXTRACTION_SYSTEM,
            )
            execution_ms = int((time.monotonic() - start_time) * 1000)

            parsed_data = self._client._parse_json(raw_response)
            if parsed_data is None:
                logger.warning("Failed to parse JSON from LLM response")
                return self._low_confidence_result(sender, subject)

            result = self._build_parsed_email(parsed_data, sender, subject)

            await self._log_extraction(
                raw_response=raw_response,
                parsed_data=parsed_data,
                confidence=result.confidence,
                execution_ms=execution_ms,
                ticket_id=ticket_id,
            )

            return result

        except Exception:
            execution_ms = int((time.monotonic() - start_time) * 1000)
            logger.exception("Email parsing failed")
            await self._log_extraction(
                raw_response="",
                parsed_data=None,
                confidence=LOW_CONFIDENCE,
                execution_ms=execution_ms,
                ticket_id=ticket_id,
                error=True,
            )
            return self._low_confidence_result(sender, subject)

    def _build_parsed_email(
        self,
        data: dict,
        sender: str,
        subject: str,
    ) -> ParsedEmail:
        deadline = None
        if data.get("deadline"):
            try:
                deadline = datetime.fromisoformat(data["deadline"])
            except (ValueError, TypeError):
                pass

        budget_hours = None
        if data.get("budget_hours") is not None:
            try:
                budget_hours = float(data["budget_hours"])
            except (ValueError, TypeError):
                pass

        overall_confidence = float(data.get("confidence", 0.0))
        overall_confidence = max(0.0, min(1.0, overall_confidence))

        return ParsedEmail(
            client=data.get("client"),
            sender=data.get("sender", sender),
            subject=data.get("subject", subject),
            project_number=data.get("project_number"),
            task_description=data.get("task_description"),
            deadline=deadline,
            budget_hours=budget_hours,
            attachments=data.get("attachments", []),
            confidence=overall_confidence,
        )

    def _low_confidence_result(self, sender: str, subject: str) -> ParsedEmail:
        return ParsedEmail(
            client=None,
            sender=sender,
            subject=subject,
            project_number=None,
            task_description=None,
            deadline=None,
            budget_hours=None,
            attachments=[],
            confidence=LOW_CONFIDENCE,
        )

    async def _log_extraction(
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
                    model=self._client._get_client().base_url.host
                    if hasattr(self._client._get_client(), "base_url")
                    else "ollama",
                    prompt_version=EMAIL_EXTRACTION_VERSION,
                    prompt=EMAIL_EXTRACTION_SYSTEM,
                    response=raw_response,
                    ticket_id=ticket_uuid,
                    parsed_json=parsed_data,
                    confidence=confidence,
                    execution_time_ms=execution_ms,
                )
                await session.commit()
        except Exception:
            logger.exception("Failed to log extraction to AILog")
