from __future__ import annotations

import json
from collections.abc import AsyncGenerator
from datetime import UTC, datetime
from pathlib import Path

import pytest
from httpx import ASGITransport, AsyncClient

from backend.app.main import app
from backend.app.services.logging import (
    SLOW_REQUEST_THRESHOLD_MS,
    RequestIDMiddleware,
    count_log_entries,
    read_log_entries,
)


def _write_test_log(log_file: Path, entries: list[dict]) -> None:
    """Write serialized log entries to a file."""
    with open(log_file, "w", encoding="utf-8") as f:
        for entry in entries:
            f.write(json.dumps(entry) + "\n")


def _make_log_entry(
    message: str = "test message",
    level: str = "INFO",
    request_id: str = "test-req-1",
    timestamp: float | None = None,
) -> dict:
    """Create a serialized loguru-style entry."""
    if timestamp is None:
        timestamp = datetime.now(tz=UTC).timestamp()
    return {
        "record": {
            "text": message,
            "message": message,
            "level": {"name": level, "no": 20},
            "name": "test_module",
            "function": "test_func",
            "line": 42,
            "time": {"timestamp": timestamp},
            "extra": {"request_id": request_id, "is_request": False},
        }
    }


class TestReadLogEntries:
    def test_reads_entries_from_file(self, tmp_path: Path) -> None:
        log_file = tmp_path / "test.log"
        entries = [_make_log_entry("hello", timestamp=1.0), _make_log_entry("world", timestamp=2.0)]
        _write_test_log(log_file, entries)

        result = read_log_entries(log_file)
        assert len(result) == 2
        assert result[0]["message"] == "world"
        assert result[1]["message"] == "hello"

    def test_returns_empty_for_missing_file(self, tmp_path: Path) -> None:
        log_file = tmp_path / "missing.log"
        result = read_log_entries(log_file)
        assert result == []

    def test_filters_by_level(self, tmp_path: Path) -> None:
        log_file = tmp_path / "test.log"
        entries = [
            _make_log_entry("info msg", level="INFO"),
            _make_log_entry("warn msg", level="WARNING"),
            _make_log_entry("error msg", level="ERROR"),
        ]
        _write_test_log(log_file, entries)

        result = read_log_entries(log_file, level="WARNING")
        assert len(result) == 2
        messages = [e["message"] for e in result]
        assert "warn msg" in messages
        assert "error msg" in messages

    def test_filters_by_search(self, tmp_path: Path) -> None:
        log_file = tmp_path / "test.log"
        entries = [
            _make_log_entry("user login failed"),
            _make_log_entry("request completed"),
            _make_log_entry("user logout"),
        ]
        _write_test_log(log_file, entries)

        result = read_log_entries(log_file, search="user")
        assert len(result) == 2

    def test_filters_by_request_id(self, tmp_path: Path) -> None:
        log_file = tmp_path / "test.log"
        entries = [
            _make_log_entry("msg1", request_id="req-aaa"),
            _make_log_entry("msg2", request_id="req-bbb"),
            _make_log_entry("msg3", request_id="req-aaa"),
        ]
        _write_test_log(log_file, entries)

        result = read_log_entries(log_file, request_id="req-aaa")
        assert len(result) == 2

    def test_pagination(self, tmp_path: Path) -> None:
        log_file = tmp_path / "test.log"
        entries = [_make_log_entry(f"msg-{i}") for i in range(10)]
        _write_test_log(log_file, entries)

        result = read_log_entries(log_file, limit=3, offset=2)
        assert len(result) == 3

    def test_sorts_by_timestamp_desc(self, tmp_path: Path) -> None:
        log_file = tmp_path / "test.log"
        entries = [
            _make_log_entry("first", timestamp=1000.0),
            _make_log_entry("third", timestamp=3000.0),
            _make_log_entry("second", timestamp=2000.0),
        ]
        _write_test_log(log_file, entries)

        result = read_log_entries(log_file)
        messages = [e["message"] for e in result]
        assert messages == ["third", "second", "first"]


class TestCountLogEntries:
    def test_counts_all_entries(self, tmp_path: Path) -> None:
        log_file = tmp_path / "test.log"
        entries = [_make_log_entry(f"msg-{i}") for i in range(5)]
        _write_test_log(log_file, entries)

        assert count_log_entries(log_file) == 5

    def test_counts_with_level_filter(self, tmp_path: Path) -> None:
        log_file = tmp_path / "test.log"
        entries = [
            _make_log_entry("info", level="INFO"),
            _make_log_entry("warn", level="WARNING"),
            _make_log_entry("error", level="ERROR"),
        ]
        _write_test_log(log_file, entries)

        assert count_log_entries(log_file, level="WARNING") == 2

    def test_counts_missing_file(self, tmp_path: Path) -> None:
        log_file = tmp_path / "missing.log"
        assert count_log_entries(log_file) == 0


class TestLogsAPI:
    @pytest.fixture
    async def client(self) -> AsyncGenerator[AsyncClient, None]:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            yield ac

    async def test_list_app_logs_returns_200(self, client: AsyncClient) -> None:
        response = await client.get("/api/logs/app")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert "offset" in data
        assert "limit" in data

    async def test_list_request_logs_returns_200(self, client: AsyncClient) -> None:
        response = await client.get("/api/logs/requests")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data

    async def test_log_stats_returns_200(self, client: AsyncClient) -> None:
        response = await client.get("/api/logs/stats")
        assert response.status_code == 200
        data = response.json()
        assert "total_entries" in data
        assert "entries_by_level" in data

    async def test_list_app_logs_accepts_filters(
        self, client: AsyncClient
    ) -> None:
        response = await client.get(
            "/api/logs/app",
            params={
                "level": "ERROR",
                "search": "test",
                "limit": 10,
                "offset": 0,
            },
        )
        assert response.status_code == 200

    async def test_list_app_logs_pagination_params(
        self, client: AsyncClient
    ) -> None:
        response = await client.get(
            "/api/logs/app", params={"limit": 5, "offset": 10}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["limit"] == 5
        assert data["offset"] == 10


class TestRequestIDMiddleware:
    def test_threshold_constant_exists(self) -> None:
        assert SLOW_REQUEST_THRESHOLD_MS == 500.0

    def test_middleware_class_exists(self) -> None:
        assert hasattr(RequestIDMiddleware, "dispatch")
