from __future__ import annotations

from datetime import datetime

from backend.app.agents.acceptance_email_agent import AcceptanceEmailAgent
from backend.app.agents.calendar_planning_agent import ScheduleBlock
from backend.app.agents.email_draft_agent import DraftEmail


class TestAcceptanceEmailAgent:
    def test_draft_acceptance(self) -> None:
        agent = AcceptanceEmailAgent()
        now = datetime.now()
        blocks = [
            ScheduleBlock(
                start_time=now.replace(hour=9, minute=0),
                end_time=now.replace(hour=13, minute=0),
                hours=4.0,
                description="Morning work block",
            )
        ]
        result = agent.draft_acceptance(
            ticket_id="550e8400-e29b-41d4-a716-446655440000",
            client="Acme Corp",
            contact="bob@example.com",
            subject="Website redesign",
            blocks=blocks,
            task_description="Redesign the website",
        )
        assert isinstance(result, DraftEmail)
        assert result.to == "bob@example.com"
        assert "4.0" in result.body
        assert "Website redesign" in result.subject

    def test_draft_decline(self) -> None:
        agent = AcceptanceEmailAgent()
        result = agent.draft_decline(
            ticket_id="550e8400-e29b-41d4-a716-446655440000",
            client="Acme Corp",
            contact="bob@example.com",
            subject="Website redesign",
            reason="Too expensive",
        )
        assert isinstance(result, DraftEmail)
        assert result.to == "bob@example.com"
        assert "Too expensive" in result.body
