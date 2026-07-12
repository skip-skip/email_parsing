from __future__ import annotations

import uuid

from backend.app.agents.calendar_planning_agent import ScheduleBlock
from backend.app.agents.email_draft_agent import DraftEmail


class AcceptanceEmailAgent:
    def draft_acceptance(
        self,
        ticket_id: str,
        client: str | None,
        contact: str | None,
        subject: str,
        blocks: list[ScheduleBlock],
        task_description: str | None = None,
    ) -> DraftEmail:
        blocks_text = "\n".join(
            f"  - {b.start_time.strftime('%Y-%m-%d %H:%M')} to {b.end_time.strftime('%H:%M')} ({b.hours}h)"
            for b in blocks
        )
        total_hours = sum(b.hours for b in blocks)

        body = (
            f"Dear {contact or client or 'Client'},\n\n"
            f"Thank you for your request regarding \"{subject}\".\n\n"
            f"We are pleased to confirm that we can proceed with this work.\n\n"
            f"Proposed Schedule:\n"
            f"{blocks_text}\n\n"
            f"Total estimated hours: {total_hours}\n\n"
            f"{'Task: ' + task_description + chr(10) + chr(10) if task_description else ''}"
            f"Please let us know if you have any questions.\n\n"
            f"Best regards"
        )

        return DraftEmail(
            to=contact or client or "",
            subject=f"Re: {subject}",
            body=body,
            missing_fields=[],
            ticket_id=uuid.UUID(ticket_id),
        )

    def draft_decline(
        self,
        ticket_id: str,
        client: str | None,
        contact: str | None,
        subject: str,
        reason: str = "We are unable to accommodate this request at this time.",
    ) -> DraftEmail:
        body = (
            f"Dear {contact or client or 'Client'},\n\n"
            f"Thank you for your request regarding \"{subject}\".\n\n"
            f"Unfortunately, we are unable to proceed with this request.\n\n"
            f"Reason: {reason}\n\n"
            f"Please let us know if you have any questions.\n\n"
            f"Best regards"
        )

        return DraftEmail(
            to=contact or client or "",
            subject=f"Re: {subject}",
            body=body,
            missing_fields=[],
            ticket_id=uuid.UUID(ticket_id),
        )
