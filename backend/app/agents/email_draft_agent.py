from __future__ import annotations

import logging
import time
import uuid
from dataclasses import dataclass

from backend.app.prompts.missing_info_draft import (
    MISSING_INFO_DRAFT_SYSTEM,
    MISSING_INFO_DRAFT_USER,
    MISSING_INFO_DRAFT_VERSION,
)
from backend.app.services.database import async_session_factory
from backend.app.services.database.repositories.ai_log_repository import AILogRepository
from backend.app.services.llm.ollama_client import OllamaClient

logger = logging.getLogger(__name__)


@dataclass
class DraftEmail:
    to: str
    subject: str
    body: str
    missing_fields: list[str]
    ticket_id: uuid.UUID
    conversation_id: str | None = None


class EmailDraftAgent:
    """Generates follow-up emails requesting missing information.

    Uses an LLM to draft a polite email that requests only the specific
    missing fields. Falls back to a template-based draft if the LLM call fails.
    """

    def __init__(self, ollama_client: OllamaClient | None = None) -> None:
        """Initialize the agent.

        Args:
            ollama_client: Ollama client for LLM calls. Creates a default if None.
        """
        self._client = ollama_client or OllamaClient()

    async def draft(
        self,
        ticket_id: str,
        sender: str,
        subject: str,
        client: str | None,
        project_number: str | None,
        task_description: str | None,
        missing_fields: list[str],
        conversation_id: str | None = None,
    ) -> DraftEmail:
        """Draft a follow-up email requesting missing information.

        Args:
            ticket_id: The associated ticket ID.
            sender: Original email sender to reply to.
            subject: Original email subject.
            client: Client name (may be None).
            project_number: Project number (may be None).
            task_description: Task description (may be None).
            missing_fields: List of field names that are missing.

        Returns:
            DraftEmail with the generated or template-based content.
        """
        missing_fields_list = "\n".join(f"- {field}" for field in missing_fields)

        user_prompt = MISSING_INFO_DRAFT_USER.format(
            sender=sender,
            subject=subject,
            missing_fields_list=missing_fields_list,
            client=client or "Unknown",
            project_number=project_number or "Not assigned",
            task_description=task_description or "Not specified",
        )

        start_time = time.monotonic()
        try:
            body = self._client.generate(
                prompt=user_prompt,
                system_prompt=MISSING_INFO_DRAFT_SYSTEM,
            )
            execution_ms = int((time.monotonic() - start_time) * 1000)

            draft = DraftEmail(
                to=sender,
                subject=f"Re: {subject}",
                body=body,
                missing_fields=missing_fields,
                ticket_id=uuid.UUID(ticket_id),
                conversation_id=conversation_id,
            )

            await self._log_draft(
                raw_response=body,
                execution_ms=execution_ms,
                ticket_id=ticket_id,
            )

            return draft

        except Exception:
            execution_ms = int((time.monotonic() - start_time) * 1000)
            logger.exception("Email draft generation failed")
            await self._log_draft(
                raw_response="",
                execution_ms=execution_ms,
                ticket_id=ticket_id,
                error=True,
            )
            return self._template_draft(
                sender, subject, missing_fields, ticket_id, conversation_id
            )

    def _template_draft(
        self,
        sender: str,
        subject: str,
        missing_fields: list[str],
        ticket_id: str,
        conversation_id: str | None = None,
    ) -> DraftEmail:
        fields_text = "\n".join(f"  - {field}" for field in missing_fields)
        body = (
            f"Dear {sender},\n\n"
            f"Thank you for your email regarding \"{subject}\".\n\n"
            f"To proceed with your request, we need the following information:\n"
            f"{fields_text}\n\n"
            f"Please provide these details at your earliest convenience.\n\n"
            f"Best regards"
        )
        return DraftEmail(
            to=sender,
            subject=f"Re: {subject}",
            body=body,
            missing_fields=missing_fields,
            ticket_id=uuid.UUID(ticket_id),
            conversation_id=conversation_id,
        )

    async def _log_draft(
        self,
        raw_response: str,
        execution_ms: int,
        ticket_id: str,
        error: bool = False,
    ) -> None:
        try:
            async with async_session_factory() as session:
                log_repo = AILogRepository(session)
                ticket_uuid = uuid.UUID(ticket_id)
                await log_repo.create(
                    model="email_draft",
                    prompt_version=MISSING_INFO_DRAFT_VERSION,
                    prompt=MISSING_INFO_DRAFT_SYSTEM,
                    response=raw_response,
                    ticket_id=ticket_uuid,
                    parsed_json={"error": error},
                    execution_time_ms=execution_ms,
                )
                await session.commit()
        except Exception:
            logger.exception("Failed to log draft to AILog")
