from __future__ import annotations

from collections.abc import AsyncGenerator
from datetime import UTC, datetime
from unittest.mock import patch

import pytest
from httpx import ASGITransport, AsyncClient

from backend.app.main import app
from backend.app.services.llm.model_manager import ModelHealthStatus


@pytest.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


class TestLLMHealthAPI:
    async def test_health_endpoint_returns_200(self, client: AsyncClient) -> None:
        with patch("backend.app.api.llm._manager") as mock_manager:
            mock_manager.check_health.return_value = {}
            mock_manager.fallback_chain = ["qwen3:8b", "llama3.3:8b", "gemma3:12b"]
            mock_manager.usage_stats.total_requests = 0
            mock_manager.usage_stats.successful_requests = 0
            mock_manager.usage_stats.failed_requests = 0
            mock_manager.usage_stats.model_counts = {}
            mock_manager.usage_stats.model_switches = []

            response = await client.get("/api/llm/health")
            assert response.status_code == 200

    async def test_health_endpoint_structure(self, client: AsyncClient) -> None:
        with patch("backend.app.api.llm._manager") as mock_manager:
            now = datetime.now(UTC)

            mock_manager.check_health.return_value = {
                "qwen3:8b": ModelHealthStatus(
                    model="qwen3:8b",
                    available=True,
                    last_checked=now,
                ),
                "llama3.3:8b": ModelHealthStatus(
                    model="llama3.3:8b",
                    available=True,
                    last_checked=now,
                ),
                "gemma3:12b": ModelHealthStatus(
                    model="gemma3:12b",
                    available=False,
                    last_checked=now,
                    last_error="Model not found",
                ),
            }
            mock_manager.fallback_chain = ["qwen3:8b", "llama3.3:8b", "gemma3:12b"]
            mock_manager.usage_stats.total_requests = 5
            mock_manager.usage_stats.successful_requests = 4
            mock_manager.usage_stats.failed_requests = 1
            mock_manager.usage_stats.model_counts = {"qwen3:8b": 4}
            mock_manager.usage_stats.model_switches = []

            response = await client.get("/api/llm/health")
            data = response.json()

            assert "status" in data
            assert "models" in data
            assert "fallback_chain" in data
            assert "usage_stats" in data
            assert data["status"] == "healthy"
            assert len(data["models"]) == 3
            assert data["models"]["qwen3:8b"]["available"] is True
            assert data["models"]["gemma3:12b"]["available"] is False
            assert data["usage_stats"]["total_requests"] == 5

    async def test_health_degraded_when_all_unavailable(
        self, client: AsyncClient
    ) -> None:
        with patch("backend.app.api.llm._manager") as mock_manager:
            mock_manager.check_health.return_value = {
                "qwen3:8b": ModelHealthStatus(
                    model="qwen3:8b",
                    available=False,
                    last_error="unavailable",
                ),
                "llama3.3:8b": ModelHealthStatus(
                    model="llama3.3:8b",
                    available=False,
                    last_error="unavailable",
                ),
                "gemma3:12b": ModelHealthStatus(
                    model="gemma3:12b",
                    available=False,
                    last_error="unavailable",
                ),
            }
            mock_manager.fallback_chain = ["qwen3:8b", "llama3.3:8b", "gemma3:12b"]
            mock_manager.usage_stats.total_requests = 0
            mock_manager.usage_stats.successful_requests = 0
            mock_manager.usage_stats.failed_requests = 0
            mock_manager.usage_stats.model_counts = {}
            mock_manager.usage_stats.model_switches = []

            response = await client.get("/api/llm/health")
            data = response.json()
            assert data["status"] == "degraded"
