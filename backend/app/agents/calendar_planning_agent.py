from __future__ import annotations

import logging
import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta

from backend.app.services.database import async_session_factory
from backend.app.services.database.repositories.ai_log_repository import AILogRepository
from backend.app.services.llm.ollama_client import OllamaClient

logger = logging.getLogger(__name__)


@dataclass
class ScheduleBlock:
    start_time: datetime
    end_time: datetime
    hours: float
    description: str = ""


@dataclass
class ScheduleSuggestion:
    blocks: list[ScheduleBlock]
    total_hours: float
    fits_deadline: bool
    confidence: float


class CalendarPlanningAgent:
    """Suggests work schedule blocks for a ticket based on deadline and budget.

    Distributes budgeted hours across available weekdays before the deadline,
    creating schedule blocks starting at 9:00 AM each day.
    """

    def __init__(self, ollama_client: OllamaClient | None = None) -> None:
        """Initialize the agent.

        Args:
            ollama_client: Ollama client (reserved for future LLM-enhanced planning).
        """
        self._client = ollama_client or OllamaClient()

    async def suggest_schedule(
        self,
        ticket_id: str,
        deadline: datetime,
        budget_hours: float,
        task_description: str,
        existing_events: list[dict] | None = None,
    ) -> ScheduleSuggestion:
        """Generate schedule blocks for a ticket.

        Distributes budgeted hours evenly across weekdays before the deadline,
        creating blocks from 9:00 AM. Skips weekends.

        Args:
            ticket_id: The ticket to schedule.
            deadline: Work must be completed by this datetime.
            budget_hours: Total hours budgeted for the task.
            task_description: Description used as block labels.
            existing_events: Pre-existing calendar events (reserved for future use).

        Returns:
            ScheduleSuggestion with proposed blocks, total hours, and confidence.
        """
        now = datetime.now()
        days_until_deadline = (deadline - now).days

        if days_until_deadline <= 0:
            return ScheduleSuggestion(
                blocks=[],
                total_hours=0,
                fits_deadline=False,
                confidence=0.0,
            )

        hours_per_day = budget_hours / max(days_until_deadline, 1)
        blocks: list[ScheduleBlock] = []

        current_date = now
        remaining_hours = budget_hours

        while remaining_hours > 0 and current_date < deadline:
            if current_date.weekday() < 5:
                day_hours = min(hours_per_day, remaining_hours, 8.0)
                if day_hours >= 0.5:
                    block = ScheduleBlock(
                        start_time=current_date.replace(hour=9, minute=0, second=0, microsecond=0),
                        end_time=current_date.replace(hour=9, minute=0, second=0, microsecond=0) + timedelta(hours=day_hours),
                        hours=day_hours,
                        description=task_description[:100] if task_description else "",
                    )
                    blocks.append(block)
                    remaining_hours -= day_hours
            current_date += timedelta(days=1)

        total_hours = sum(b.hours for b in blocks)
        fits_deadline = remaining_hours <= 0

        suggestion = ScheduleSuggestion(
            blocks=blocks,
            total_hours=total_hours,
            fits_deadline=fits_deadline,
            confidence=0.8 if fits_deadline else 0.4,
        )

        await self._log_suggestion(
            ticket_id=ticket_id,
            suggestion=suggestion,
        )

        return suggestion

    async def _log_suggestion(
        self,
        ticket_id: str,
        suggestion: ScheduleSuggestion,
    ) -> None:
        try:
            ticket_uuid = uuid.UUID(ticket_id)
        except (ValueError, AttributeError):
            return
        try:
            async with async_session_factory() as session:
                log_repo = AILogRepository(session)
                await log_repo.create(
                    model="calendar_planning",
                    prompt_version="v1.0.0",
                    prompt="schedule_suggestion",
                    response=f"blocks={len(suggestion.blocks)}, hours={suggestion.total_hours}",
                    ticket_id=ticket_uuid,
                    parsed_json={
                        "total_hours": suggestion.total_hours,
                        "fits_deadline": suggestion.fits_deadline,
                        "num_blocks": len(suggestion.blocks),
                    },
                    confidence=suggestion.confidence,
                )
                await session.commit()
        except Exception:
            logger.exception("Failed to log schedule suggestion")
