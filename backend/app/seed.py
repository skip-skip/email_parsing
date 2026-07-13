"""Seed the development database with realistic sample data.

Usage:
    python -m backend.app.seed              # Default: 50 tickets
    python -m backend.app.seed --count 100  # 100 tickets
    python -m backend.app.seed --clear      # Clear existing data first
"""

from __future__ import annotations

import argparse
import asyncio
import random
import uuid
from datetime import datetime, timedelta

from sqlalchemy import delete

from backend.app.models import AILog, CalendarEvent, Email, Ticket
from backend.app.services.database import async_session_factory, init_db

CLIENTS: list[dict[str, str]] = [
    {"client": "Acme Corp", "domain": "acme.com"},
    {"client": "TechVista Solutions", "domain": "techvista.io"},
    {"client": "GreenLeaf Landscaping", "domain": "greenleaf.com"},
    {"client": "BrightPath Education", "domain": "brightpath.edu"},
    {"client": "Summit Construction", "domain": "summitbuild.com"},
    {"client": "Harbor Digital", "domain": "harbordigital.com"},
    {"client": "Cascade Media Group", "domain": "cascademedia.com"},
    {"client": "Northwind Traders", "domain": "northwind.com"},
    {"client": "BlueSky Analytics", "domain": "bluesky.io"},
    {"client": "Ironclad Security", "domain": "ironclad.io"},
    {"client": "Pinnacle Health", "domain": "pinnacle.health"},
    {"client": "VeloWorks Engineering", "domain": "veloworks.com"},
]

TASK_TEMPLATES: list[dict[str, str]] = [
    {
        "description": "Design and implement a responsive landing page for the upcoming product launch",
        "subject": "Landing Page Design Request",
        "body": (
            "Hi, we need a new landing page designed for our Q3 product launch. "
            "It should be responsive and follow our brand guidelines. "
            "Please estimate hours and let us know your availability."
        ),
    },
    {
        "description": "Migrate legacy database from MySQL to PostgreSQL with zero downtime",
        "subject": "Database Migration Project",
        "body": (
            "We need to migrate our production database from MySQL 5.7 to PostgreSQL 16. "
            "The database has approximately 2TB of data. Zero downtime is critical. "
            "Please provide a detailed migration plan."
        ),
    },
    {
        "description": "Build automated email notification system for customer onboarding",
        "subject": "Email Automation System",
        "body": (
            "We are looking to build an automated email notification system for our "
            "customer onboarding flow. It should support templates, scheduling, "
            "and tracking. Can you provide an estimate?"
        ),
    },
    {
        "description": "Create a real-time analytics dashboard with WebSocket integration",
        "subject": "Analytics Dashboard Project",
        "body": (
            "We need a real-time analytics dashboard that displays KPIs and user "
            "engagement metrics. Data should update in real-time via WebSockets. "
            "Please estimate the effort."
        ),
    },
    {
        "description": "Implement OAuth2 authentication with role-based access control",
        "subject": "Auth System Implementation",
        "body": (
            "We need OAuth2 authentication implemented with support for Google and "
            "Microsoft SSO, plus role-based access control. Our app is built with "
            "FastAPI and React. Please provide a timeline."
        ),
    },
    {
        "description": "Develop a customer support chatbot using retrieval-augmented generation",
        "subject": "AI Chatbot Development",
        "body": (
            "We want to build a customer support chatbot that can answer questions "
            "from our knowledge base using RAG. It should integrate with our existing "
            "ticketing system. What is the estimated effort?"
        ),
    },
    {
        "description": "Set up CI/CD pipeline with automated testing and deployment",
        "subject": "CI/CD Pipeline Setup",
        "body": (
            "We need a complete CI/CD pipeline set up for our monorepo. "
            "Include automated unit tests, integration tests, linting, and "
            "deployment to staging and production environments."
        ),
    },
    {
        "description": "Redesign the mobile app navigation and improve accessibility",
        "subject": "Mobile App UX Redesign",
        "body": (
            "Our mobile app navigation needs a complete redesign to improve "
            "usability and meet WCAG 2.1 AA accessibility standards. "
            "Please review the current app and propose improvements."
        ),
    },
    {
        "description": "Build a data pipeline to aggregate metrics from multiple microservices",
        "subject": "Data Pipeline Architecture",
        "body": (
            "We need a data pipeline that aggregates metrics from our 12 "
            "microservices into a central analytics platform. Data should be "
            "processed in near real-time. Please provide an architecture proposal."
        ),
    },
    {
        "description": "Implement rate limiting and request throttling on the public API",
        "subject": "API Rate Limiting",
        "body": (
            "We are experiencing abuse on our public API and need rate limiting "
            "implemented urgently. We need per-user and per-endpoint throttling "
            "with configurable limits. Please provide an estimate."
        ),
    },
    {
        "description": "Create a webhook system for third-party integrations",
        "subject": "Webhook System Design",
        "body": (
            "We need to build a webhook system that allows third-party services "
            "to subscribe to events from our platform. It should support "
            "retries, dead letter queues, and an admin dashboard."
        ),
    },
    {
        "description": "Optimize search performance for the product catalog",
        "subject": "Search Optimization",
        "body": (
            "Our product catalog search is slow with over 500K products. "
            "We need to implement full-text search with filtering, sorting, "
            "and autocomplete. Please evaluate Elasticsearch vs Meilisearch."
        ),
    },
]

STATUSES = ["NEW", "PARSED", "VALIDATED", "WAITING_FOR_INFORMATION",
            "READY_FOR_SCHEDULING", "PENDING_USER_APPROVAL", "ACCEPTED",
            "CALENDAR_CREATED", "IN_PROGRESS", "COMPLETED"]

CALENDAR_STATUSES = ["PROPOSED", "CONFIRMED", "CANCELLED"]

AI_MODELS = ["qwen3:8b", "gemma3:12b", "llama3.3:8b"]

PROMPT_VERSIONS = ["v1.0", "v1.1", "v2.0", "v2.1"]

PROMPT_TEMPLATES = [
    "Extract task information from the following email:\n\n{body}",
    "Analyze the following email and extract key fields:\n\n{body}",
    "Parse this email for project details:\n\n{body}",
]

RESPONSE_TEMPLATES = [
    '{{"client": "{client}", "project_number": "{project}", "deadline": "{deadline}", "budget_hours": {hours}, "confidence": {confidence}}}',
    '{{"client": "{client}", "project_number": "{project}", "task_description": "{desc}", "confidence": {confidence}}}',
]


def _random_name() -> str:
    first_names = ["James", "Sarah", "Michael", "Emily", "David", "Jessica",
                   "Robert", "Jennifer", "William", "Linda", "Richard", "Patricia"]
    last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia",
                  "Miller", "Davis", "Rodriguez", "Martinez", "Anderson", "Taylor"]
    return f"{random.choice(first_names)} {random.choice(last_names)}"


def _generate_project_number(client_name: str) -> str:
    prefix = "".join(c for c in client_name if c.isupper())[:4]
    if len(prefix) < 2:
        prefix = client_name[:4].upper()
    return f"{prefix}-{random.randint(100, 999)}"


def _generate_ticket(
    index: int,
    base_time: datetime,
) -> Ticket:
    client_info = random.choice(CLIENTS)
    task = random.choice(TASK_TEMPLATES)
    status = random.choice(STATUSES)
    project_number = _generate_project_number(client_info["client"])

    days_ago = random.randint(0, 60)
    created = base_time - timedelta(days=days_ago, hours=random.randint(0, 23))
    deadline = created + timedelta(days=random.randint(3, 30))

    return Ticket(
        ticket_id=uuid.uuid4(),
        status=status,
        client=client_info["client"],
        contact=f"{_random_name().lower().replace(' ', '.')}@{client_info['domain']}",
        project_number=project_number,
        task_description=task["description"],
        deadline=deadline,
        budget_hours=round(random.uniform(4.0, 80.0), 1),
        estimated_hours=round(random.uniform(4.0, 80.0), 1) if status not in ("NEW", "PARSED") else None,
        priority=random.randint(0, 4),
        calendar_event_id=None,
        conversation_id=f"conv-{uuid.uuid4().hex[:12]}",
        created_at=created,
        updated_at=created + timedelta(hours=random.randint(1, 48)) if random.random() > 0.3 else None,
    )


def _generate_emails(
    ticket: Ticket,
    task: dict[str, str],
    client_info: dict[str, str],
) -> list[Email]:
    email_count = random.choices([1, 2, 3], weights=[50, 35, 15])[0]
    emails = []
    base_time = ticket.created_at

    for i in range(email_count):
        received = base_time + timedelta(hours=i * random.randint(4, 72))
        is_reply = i > 0
        body = task["body"] if not is_reply else (
            f"Thanks for getting back to us. Here is the additional information you requested:\n\n"
            f"Project timeline: {random.randint(2, 8)} weeks\n"
            f"Team size: {random.randint(2, 5)} people\n"
            f"Budget approval: confirmed"
        )

        emails.append(Email(
            email_id=uuid.uuid4(),
            conversation_id=ticket.conversation_id,
            entry_id=f"outlook-entry-{uuid.uuid4().hex[:16]}",
            sender=ticket.contact if is_reply else f"sender@{client_info['domain']}",
            subject=f"Re: {task['subject']}" if is_reply else task["subject"],
            body=body,
            received_time=received,
            attachments=[],
            ticket_id=ticket.ticket_id,
        ))

    return emails


def _generate_calendar_event(ticket: Ticket) -> CalendarEvent | None:
    if ticket.status not in ("READY_FOR_SCHEDULING", "PENDING_USER_APPROVAL",
                              "ACCEPTED", "CALENDAR_CREATED", "IN_PROGRESS", "COMPLETED"):
        return None

    hours = ticket.budget_hours or random.uniform(4.0, 20.0)
    deadline = ticket.deadline or datetime.now() + timedelta(days=14)
    start = deadline - timedelta(days=random.randint(1, 5), hours=1)
    end = start + timedelta(hours=hours)

    return CalendarEvent(
        calendar_event_id=uuid.uuid4(),
        ticket_id=ticket.ticket_id,
        outlook_event_id=f"outlook-event-{uuid.uuid4().hex[:8]}" if random.random() > 0.4 else None,
        start_time=start,
        end_time=end,
        duration=hours,
        status=random.choice(CALENDAR_STATUSES),
        created_at=ticket.created_at + timedelta(hours=random.randint(1, 24)),
    )


def _generate_ai_logs(ticket: Ticket, task: dict[str, str]) -> list[AILog]:
    log_count = random.choices([1, 2, 3], weights=[40, 40, 20])[0]
    logs = []
    base_time = ticket.created_at + timedelta(minutes=random.randint(5, 30))

    for i in range(log_count):
        model = random.choice(AI_MODELS)
        prompt_version = random.choice(PROMPT_VERSIONS)
        prompt = random.choice(PROMPT_TEMPLATES).format(body=task["body"][:200])
        confidence = round(random.uniform(0.45, 0.99), 3)
        success = random.random() > 0.1

        parsed = {
            "client": ticket.client,
            "project_number": ticket.project_number,
            "confidence": confidence,
        }

        response = random.choice(RESPONSE_TEMPLATES).format(
            client=ticket.client or "Unknown",
            project=ticket.project_number or "UNKNOWN-000",
            deadline=str(ticket.deadline.date()) if ticket.deadline else "TBD",
            hours=ticket.budget_hours or 0,
            desc=(ticket.task_description or "No description")[:50],
            confidence=confidence,
        )

        logs.append(AILog(
            log_id=uuid.uuid4(),
            ticket_id=ticket.ticket_id,
            model=model,
            prompt_version=prompt_version,
            prompt=prompt,
            response=response if success else "",
            parsed_json=parsed if success else None,
            confidence=confidence if success else None,
            input_tokens=random.randint(100, 2000),
            output_tokens=random.randint(50, 1000) if success else None,
            success=success,
            error_message=None if success else "Model overloaded, try again later",
            execution_time_ms=random.randint(200, 5000),
            created_at=base_time + timedelta(minutes=i * random.randint(1, 10)),
        ))

    return logs


async def seed(count: int = 50, clear: bool = False) -> None:
    await init_db()

    async with async_session_factory() as session:
        if clear:
            await session.execute(delete(AILog))
            await session.execute(delete(CalendarEvent))
            await session.execute(delete(Email))
            await session.execute(delete(Ticket))
            await session.commit()

        base_time = datetime.now()
        all_emails: list[Email] = []
        all_calendar_events: list[CalendarEvent] = []
        all_ai_logs: list[AILog] = []

        for i in range(count):
            ticket = _generate_ticket(i, base_time)
            session.add(ticket)

            client_info = next(
                (c for c in CLIENTS if c["client"] == ticket.client),
                CLIENTS[0],
            )
            task = random.choice(TASK_TEMPLATES)

            emails = _generate_emails(ticket, task, client_info)
            all_emails.extend(emails)

            cal_event = _generate_calendar_event(ticket)
            if cal_event:
                all_calendar_events.append(cal_event)

            ai_logs = _generate_ai_logs(ticket, task)
            all_ai_logs.extend(ai_logs)

        for email in all_emails:
            session.add(email)
        for event in all_calendar_events:
            session.add(event)
        for log in all_ai_logs:
            session.add(log)

        await session.commit()

        print("Seed data inserted successfully:")
        print(f"  Tickets:          {count}")
        print(f"  Emails:           {len(all_emails)}")
        print(f"  Calendar Events:  {len(all_calendar_events)}")
        print(f"  AI Logs:          {len(all_ai_logs)}")
        print(f"  Total records:    {count + len(all_emails) + len(all_calendar_events) + len(all_ai_logs)}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Seed the development database")
    parser.add_argument("--count", type=int, default=50, help="Number of tickets to create")
    parser.add_argument("--clear", action="store_true", help="Clear existing data before seeding")
    args = parser.parse_args()

    asyncio.run(seed(count=args.count, clear=args.clear))


if __name__ == "__main__":
    main()
