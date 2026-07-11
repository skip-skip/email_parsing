"""Seed the development database with sample data."""

import asyncio
import uuid
from datetime import datetime, timedelta

from backend.app.models import AILog, CalendarEvent, Email, Ticket
from backend.app.services.database import async_session_factory, init_db


async def seed() -> None:
    await init_db()

    async with async_session_factory() as session:
        ticket_id = uuid.uuid4()
        ticket = Ticket(
            ticket_id=ticket_id,
            status="NEW",
            client="Acme Corp",
            contact="john@acme.com",
            project_number="ACME-001",
            task_description="Build a new landing page for the Q3 campaign",
            deadline=datetime.now() + timedelta(days=14),
            budget_hours=20.0,
            priority=1,
            conversation_id="conv-abc-123",
        )
        session.add(ticket)

        email = Email(
            email_id=uuid.uuid4(),
            conversation_id="conv-abc-123",
            entry_id="outlook-entry-001",
            sender="john@acme.com",
            subject="Landing Page Request",
            body="Hi, we need a new landing page for our Q3 campaign. Please estimate hours and schedule.",
            received_time=datetime.now() - timedelta(hours=2),
            attachments=[],
            ticket_id=ticket_id,
        )
        session.add(email)

        calendar_event = CalendarEvent(
            calendar_event_id=uuid.uuid4(),
            ticket_id=ticket_id,
            start_time=datetime.now() + timedelta(days=1),
            end_time=datetime.now() + timedelta(days=1, hours=3),
            duration=3.0,
            status="PROPOSED",
        )
        session.add(calendar_event)

        ai_log = AILog(
            log_id=uuid.uuid4(),
            ticket_id=ticket_id,
            model="qwen3:8b",
            prompt_version="v1.0",
            prompt="Extract task information from this email...",
            response='{"client": "Acme Corp", "project_number": "ACME-001"}',
            parsed_json={"client": "Acme Corp", "project_number": "ACME-001"},
            confidence=0.92,
            execution_time_ms=1250,
        )
        session.add(ai_log)

        await session.commit()
        print("Seed data inserted successfully.")


if __name__ == "__main__":
    asyncio.run(seed())
