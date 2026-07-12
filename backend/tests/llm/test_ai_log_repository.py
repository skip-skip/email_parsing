from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta

import pytest

from backend.app.services.database.repositories.ai_log_repository import AILogRepository


class TestAILogRepository:
    async def test_create_log(self, db_session: object) -> None:
        repo = AILogRepository(db_session)  # type: ignore[arg-type]
        log = await repo.create(
            model="qwen3:8b",
            prompt_version="v1",
            prompt="test prompt",
            response="test response",
        )
        assert log.log_id is not None
        assert log.model == "qwen3:8b"
        assert log.prompt_version == "v1"
        assert log.success is True
        assert log.input_tokens is None
        assert log.output_tokens is None
        assert log.error_message is None

    async def test_create_log_with_new_fields(self, db_session: object) -> None:
        repo = AILogRepository(db_session)  # type: ignore[arg-type]
        log = await repo.create(
            model="qwen3:8b",
            prompt_version="v1",
            prompt="test prompt",
            response="test response",
            input_tokens=100,
            output_tokens=50,
            success=False,
            error_message="Connection timeout",
            execution_time_ms=1500,
        )
        assert log.input_tokens == 100
        assert log.output_tokens == 50
        assert log.success is False
        assert log.error_message == "Connection timeout"
        assert log.execution_time_ms == 1500

    async def test_get_by_ticket_id(self, db_session: object) -> None:
        ticket_id = uuid.uuid4()
        repo = AILogRepository(db_session)  # type: ignore[arg-type]
        await repo.create(
            model="qwen3:8b",
            prompt_version="v1",
            prompt="prompt 1",
            response="response 1",
            ticket_id=ticket_id,
        )
        await repo.create(
            model="qwen3:8b",
            prompt_version="v1",
            prompt="prompt 2",
            response="response 2",
            ticket_id=ticket_id,
        )
        await repo.create(
            model="qwen3:8b",
            prompt_version="v1",
            prompt="prompt 3",
            response="response 3",
            ticket_id=uuid.uuid4(),
        )
        logs = await repo.get_by_ticket_id(ticket_id)
        assert len(logs) == 2

    async def test_list_logs_pagination(self, db_session: object) -> None:
        repo = AILogRepository(db_session)  # type: ignore[arg-type]
        for i in range(5):
            await repo.create(
                model="qwen3:8b",
                prompt_version="v1",
                prompt=f"prompt {i}",
                response=f"response {i}",
            )
        page1 = await repo.list_logs(offset=0, limit=2)
        assert len(page1) == 2
        page2 = await repo.list_logs(offset=2, limit=2)
        assert len(page2) == 2
        page3 = await repo.list_logs(offset=4, limit=2)
        assert len(page3) == 1

    async def test_list_logs_filter_by_model(self, db_session: object) -> None:
        repo = AILogRepository(db_session)  # type: ignore[arg-type]
        await repo.create(
            model="qwen3:8b", prompt_version="v1", prompt="p1", response="r1"
        )
        await repo.create(
            model="gemma3:12b", prompt_version="v1", prompt="p2", response="r2"
        )
        logs = await repo.list_logs(model="qwen3:8b")
        assert len(logs) == 1
        assert logs[0].model == "qwen3:8b"

    async def test_list_logs_filter_by_success(self, db_session: object) -> None:
        repo = AILogRepository(db_session)  # type: ignore[arg-type]
        await repo.create(
            model="qwen3:8b",
            prompt_version="v1",
            prompt="p1",
            response="r1",
            success=True,
        )
        await repo.create(
            model="qwen3:8b",
            prompt_version="v1",
            prompt="p2",
            response="r2",
            success=False,
        )
        success_logs = await repo.list_logs(success=True)
        assert len(success_logs) == 1
        failed_logs = await repo.list_logs(success=False)
        assert len(failed_logs) == 1

    async def test_list_logs_filter_by_date_range(self, db_session: object) -> None:
        repo = AILogRepository(db_session)  # type: ignore[arg-type]
        now = datetime.now(UTC)
        await repo.create(
            model="qwen3:8b",
            prompt_version="v1",
            prompt="p1",
            response="r1",
        )
        logs = await repo.list_logs(date_from=now - timedelta(hours=1))
        assert len(logs) == 1
        logs = await repo.list_logs(date_from=now + timedelta(hours=1))
        assert len(logs) == 0

    async def test_count_logs(self, db_session: object) -> None:
        repo = AILogRepository(db_session)  # type: ignore[arg-type]
        for i in range(3):
            await repo.create(
                model="qwen3:8b",
                prompt_version="v1",
                prompt=f"p{i}",
                response=f"r{i}",
            )
        total = await repo.count_logs()
        assert total == 3

    async def test_get_stats(self, db_session: object) -> None:
        repo = AILogRepository(db_session)  # type: ignore[arg-type]
        await repo.create(
            model="qwen3:8b",
            prompt_version="v1",
            prompt="p1",
            response="r1",
            success=True,
            execution_time_ms=100,
            confidence=0.9,
            input_tokens=50,
            output_tokens=25,
        )
        await repo.create(
            model="qwen3:8b",
            prompt_version="v1",
            prompt="p2",
            response="r2",
            success=False,
            execution_time_ms=200,
            error_message="timeout",
            input_tokens=30,
            output_tokens=0,
        )
        await repo.create(
            model="gemma3:12b",
            prompt_version="v2",
            prompt="p3",
            response="r3",
            success=True,
            execution_time_ms=300,
            confidence=0.8,
            input_tokens=40,
            output_tokens=20,
        )
        stats = await repo.get_stats()
        assert stats["total_interactions"] == 3
        assert stats["successful_interactions"] == 2
        assert stats["failed_interactions"] == 1
        assert stats["success_rate"] == pytest.approx(66.67, abs=0.01)
        assert stats["avg_execution_time_ms"] == pytest.approx(200.0)
        assert stats["avg_confidence"] == pytest.approx(0.85)
        assert stats["total_input_tokens"] == 120
        assert stats["total_output_tokens"] == 45
        assert stats["model_counts"]["qwen3:8b"] == 2
        assert stats["model_counts"]["gemma3:12b"] == 1

    async def test_get_stats_empty(self, db_session: object) -> None:
        repo = AILogRepository(db_session)  # type: ignore[arg-type]
        stats = await repo.get_stats()
        assert stats["total_interactions"] == 0
        assert stats["success_rate"] == 0.0
        assert stats["avg_execution_time_ms"] == 0.0
