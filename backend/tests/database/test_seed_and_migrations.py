"""Tests for the seed data script and migration verification."""

from __future__ import annotations

from datetime import datetime

import pytest
from sqlalchemy import inspect, text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from backend.app.models import AILog, CalendarEvent, Email, Ticket
from backend.app.services.database.base import Base


@pytest.fixture
async def memory_engine():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest.fixture
async def memory_session(memory_engine):
    factory = sessionmaker(memory_engine, class_=AsyncSession, expire_on_commit=False)
    async with factory() as session:
        yield session


class TestSeedDataGeneration:
    def test_seed_imports(self):
        from backend.app.seed import (
            CLIENTS,
            TASK_TEMPLATES,
        )

        assert len(CLIENTS) > 0
        assert len(TASK_TEMPLATES) > 0

    def test_generate_project_number(self):
        from backend.app.seed import _generate_project_number

        result = _generate_project_number("Acme Corp")
        assert "-" in result
        assert len(result.split("-")[1]) == 3

    def test_generate_project_number_short_name(self):
        from backend.app.seed import _generate_project_number

        result = _generate_project_number("AB")
        assert "-" in result

    def test_generate_ticket_returns_ticket(self):
        from backend.app.seed import _generate_ticket

        ticket = _generate_ticket(0, datetime.now())
        assert isinstance(ticket, Ticket)
        assert ticket.client is not None
        assert ticket.conversation_id is not None
        assert ticket.created_at is not None

    def test_generate_ticket_unique_ids(self):
        from backend.app.seed import _generate_ticket

        base = datetime.now()
        tickets = [_generate_ticket(i, base) for i in range(10)]
        ids = {t.ticket_id for t in tickets}
        assert len(ids) == 10

    def test_generate_emails_returns_list(self):
        from backend.app.seed import _generate_emails, _generate_ticket

        ticket = _generate_ticket(0, datetime.now())
        emails = _generate_emails(
            ticket,
            {"body": "test body", "subject": "Test"},
            {"client": "Test", "domain": "test.com"},
        )
        assert isinstance(emails, list)
        assert len(emails) >= 1
        for email in emails:
            assert isinstance(email, Email)
            assert email.ticket_id == ticket.ticket_id
            assert email.conversation_id == ticket.conversation_id

    def test_generate_calendar_event_completed_status(self):
        from backend.app.seed import _generate_calendar_event, _generate_ticket

        ticket = _generate_ticket(0, datetime.now())
        ticket.status = "ACCEPTED"
        event = _generate_calendar_event(ticket)
        assert event is not None
        assert isinstance(event, CalendarEvent)
        assert event.ticket_id == ticket.ticket_id

    def test_generate_calendar_event_new_status(self):
        from backend.app.seed import _generate_calendar_event, _generate_ticket

        ticket = _generate_ticket(0, datetime.now())
        ticket.status = "NEW"
        event = _generate_calendar_event(ticket)
        assert event is None

    def test_generate_ai_logs_returns_list(self):
        from backend.app.seed import _generate_ai_logs, _generate_ticket

        ticket = _generate_ticket(0, datetime.now())
        logs = _generate_ai_logs(ticket, {"body": "test body"})
        assert isinstance(logs, list)
        assert len(logs) >= 1
        for log in logs:
            assert isinstance(log, AILog)
            assert log.ticket_id == ticket.ticket_id

    def test_generate_ai_logs_success_rate(self):
        from backend.app.seed import _generate_ai_logs, _generate_ticket

        ticket = _generate_ticket(0, datetime.now())
        logs = []
        for _ in range(50):
            logs.extend(_generate_ai_logs(ticket, {"body": "test"}))

        success_count = sum(1 for log in logs if log.success)
        assert success_count > len(logs) * 0.5, "Expected most logs to be successful"


class TestSeedIntegration:
    @pytest.mark.asyncio
    async def test_seed_creates_records(self, memory_engine):
        from backend.app.seed import (
            CLIENTS,
            TASK_TEMPLATES,
            _generate_ai_logs,
            _generate_calendar_event,
            _generate_emails,
            _generate_ticket,
        )

        factory = sessionmaker(memory_engine, class_=AsyncSession, expire_on_commit=False)

        async with factory() as session:
            base_time = datetime.now()
            ticket_count = 5

            for i in range(ticket_count):
                ticket = _generate_ticket(i, base_time)
                session.add(ticket)

                client_info = next(
                    (c for c in CLIENTS if c["client"] == ticket.client),
                    CLIENTS[0],
                )
                task = TASK_TEMPLATES[i % len(TASK_TEMPLATES)]

                for email in _generate_emails(ticket, task, client_info):
                    session.add(email)

                cal_event = _generate_calendar_event(ticket)
                if cal_event:
                    session.add(cal_event)

                for log in _generate_ai_logs(ticket, task):
                    session.add(log)

            await session.commit()

            result = await session.execute(text("SELECT COUNT(*) FROM tickets"))
            assert result.scalar_one() == ticket_count

            result = await session.execute(text("SELECT COUNT(*) FROM emails"))
            assert result.scalar_one() > 0

    @pytest.mark.asyncio
    async def test_ticket_has_expected_columns(self, memory_engine):
        factory = sessionmaker(memory_engine, class_=AsyncSession, expire_on_commit=False)

        async with factory() as session:
            result = await session.execute(
                text("PRAGMA table_info(tickets)")
            )
            columns = {row[1] for row in result.fetchall()}
            expected = {
                "ticket_id", "status", "client", "contact", "project_number",
                "task_description", "deadline", "budget_hours", "estimated_hours",
                "priority", "calendar_event_id", "conversation_id",
                "created_at", "updated_at",
            }
            assert expected.issubset(columns)

    @pytest.mark.asyncio
    async def test_email_has_expected_columns(self, memory_engine):
        factory = sessionmaker(memory_engine, class_=AsyncSession, expire_on_commit=False)

        async with factory() as session:
            result = await session.execute(
                text("PRAGMA table_info(emails)")
            )
            columns = {row[1] for row in result.fetchall()}
            expected = {
                "email_id", "conversation_id", "entry_id", "sender",
                "subject", "body", "received_time", "attachments",
                "created_at", "ticket_id",
            }
            assert expected.issubset(columns)

    @pytest.mark.asyncio
    async def test_calendar_event_has_expected_columns(self, memory_engine):
        factory = sessionmaker(memory_engine, class_=AsyncSession, expire_on_commit=False)

        async with factory() as session:
            result = await session.execute(
                text("PRAGMA table_info(calendar_events)")
            )
            columns = {row[1] for row in result.fetchall()}
            expected = {
                "calendar_event_id", "ticket_id", "outlook_event_id",
                "start_time", "end_time", "duration", "status", "created_at",
            }
            assert expected.issubset(columns)

    @pytest.mark.asyncio
    async def test_ai_log_has_expected_columns(self, memory_engine):
        factory = sessionmaker(memory_engine, class_=AsyncSession, expire_on_commit=False)

        async with factory() as session:
            result = await session.execute(
                text("PRAGMA table_info(ai_logs)")
            )
            columns = {row[1] for row in result.fetchall()}
            expected = {
                "log_id", "ticket_id", "model", "prompt_version", "prompt",
                "response", "parsed_json", "confidence", "execution_time_ms",
                "created_at", "input_tokens", "output_tokens", "success",
                "error_message",
            }
            assert expected.issubset(columns)


class TestModelIndexes:
    @pytest.mark.asyncio
    async def test_ticket_indexes_exist(self, memory_engine):
        async with memory_engine.connect() as conn:
            result = await conn.run_sync(
                lambda sync_conn: [
                    idx["name"]
                    for idx in inspect(sync_conn).get_indexes("tickets")
                    if idx["name"]
                ]
            )
            expected = [
                "ix_tickets_status", "ix_tickets_conversation_id",
                "ix_tickets_client", "ix_tickets_deadline", "ix_tickets_priority",
            ]
            for idx in expected:
                assert idx in result, f"Missing index: {idx}"

    @pytest.mark.asyncio
    async def test_email_indexes_exist(self, memory_engine):
        async with memory_engine.connect() as conn:
            result = await conn.run_sync(
                lambda sync_conn: [
                    idx["name"]
                    for idx in inspect(sync_conn).get_indexes("emails")
                    if idx["name"]
                ]
            )
            expected = [
                "ix_emails_conversation_id", "ix_emails_ticket_id",
                "ix_emails_sender", "ix_emails_received_time",
            ]
            for idx in expected:
                assert idx in result, f"Missing index: {idx}"

    @pytest.mark.asyncio
    async def test_calendar_event_indexes_exist(self, memory_engine):
        async with memory_engine.connect() as conn:
            result = await conn.run_sync(
                lambda sync_conn: [
                    idx["name"]
                    for idx in inspect(sync_conn).get_indexes("calendar_events")
                    if idx["name"]
                ]
            )
            expected = [
                "ix_calendar_events_ticket_id", "ix_calendar_events_status",
                "ix_calendar_events_start_time",
            ]
            for idx in expected:
                assert idx in result, f"Missing index: {idx}"

    @pytest.mark.asyncio
    async def test_ai_log_indexes_exist(self, memory_engine):
        async with memory_engine.connect() as conn:
            result = await conn.run_sync(
                lambda sync_conn: [
                    idx["name"]
                    for idx in inspect(sync_conn).get_indexes("ai_logs")
                    if idx["name"]
                ]
            )
            expected = [
                "ix_ai_logs_ticket_id", "ix_ai_logs_created_at",
                "ix_ai_logs_success", "ix_ai_logs_model", "ix_ai_logs_confidence",
            ]
            for idx in expected:
                assert idx in result, f"Missing index: {idx}"


class TestSeedCLI:
    def test_seed_main_function_exists(self):
        from backend.app.seed import main

        assert callable(main)

    def test_verify_migrations_main_function_exists(self):
        from backend.app.verify_migrations import main

        assert callable(main)

    def test_verify_migrations_function_exists(self):
        from backend.app.verify_migrations import verify_migrations

        assert callable(verify_migrations)
