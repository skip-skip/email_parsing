from __future__ import annotations

import time

import pytest

from backend.app.services.llm.ai_logger import AILogger, log_interaction, measure_time


class TestMeasureTime:
    def test_measure_time_captures_elapsed(self) -> None:
        with measure_time() as result:
            time.sleep(0.01)
        assert result["elapsed_ms"] is not None
        assert result["elapsed_ms"] >= 10

    def test_measure_time_with_exception(self) -> None:
        with pytest.raises(ValueError):
            with measure_time() as result:
                raise ValueError("test")
        assert result["elapsed_ms"] is not None


class TestLogInteraction:
    async def test_log_interaction_creates_record(self, db_session: object) -> None:
        log = await log_interaction(
            db_session,  # type: ignore[arg-type]
            model="qwen3:8b",
            prompt_version="v1",
            prompt="What is the task?",
            response="Extract task info",
        )
        assert log.log_id is not None
        assert log.model == "qwen3:8b"
        assert log.success is True

    async def test_log_interaction_with_all_fields(self, db_session: object) -> None:
        log = await log_interaction(
            db_session,  # type: ignore[arg-type]
            model="qwen3:8b",
            prompt_version="v2",
            prompt="Extract",
            response='{"task": "test"}',
            parsed_json={"task": "test"},
            confidence=0.85,
            execution_time_ms=1500,
            input_tokens=100,
            output_tokens=50,
            success=True,
        )
        assert log.parsed_json == {"task": "test"}
        assert log.confidence == 0.85
        assert log.execution_time_ms == 1500
        assert log.input_tokens == 100
        assert log.output_tokens == 50

    async def test_log_interaction_failure(self, db_session: object) -> None:
        log = await log_interaction(
            db_session,  # type: ignore[arg-type]
            model="qwen3:8b",
            prompt_version="v1",
            prompt="test",
            response="",
            success=False,
            error_message="Connection refused",
        )
        assert log.success is False
        assert log.error_message == "Connection refused"


class TestAILogger:
    async def test_logger_creates_record(self, db_session: object) -> None:
        logger = AILogger(db_session)  # type: ignore[arg-type]
        log = await logger.log(
            model="qwen3:8b",
            prompt_version="v1",
            prompt="test",
            response="result",
        )
        assert log.log_id is not None
        assert log.model == "qwen3:8b"

    async def test_logger_with_tokens(self, db_session: object) -> None:
        logger = AILogger(db_session)  # type: ignore[arg-type]
        log = await logger.log(
            model="qwen3:8b",
            prompt_version="v1",
            prompt="test",
            response="result",
            input_tokens=200,
            output_tokens=100,
        )
        assert log.input_tokens == 200
        assert log.output_tokens == 100
