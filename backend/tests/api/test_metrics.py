from __future__ import annotations

from collections.abc import AsyncGenerator

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from backend.app.main import app
from backend.app.services.database import get_db
from backend.app.services.database.base import Base
from backend.app.services.metrics import get_metrics


@pytest.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(engine, expire_on_commit=False)

    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        async with session_factory() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()
    await engine.dispose()


class TestHealthCheck:
    async def test_health_check_returns_ok(self, client: AsyncClient) -> None:
        response = await client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "uptime_seconds" in data
        assert data["database"] == "connected"

    async def test_health_check_has_uptime(self, client: AsyncClient) -> None:
        response = await client.get("/health")
        data = response.json()
        assert isinstance(data["uptime_seconds"], float)
        assert data["uptime_seconds"] >= 0


class TestMetricsEndpoint:
    async def test_metrics_returns_structure(self, client: AsyncClient) -> None:
        response = await client.get("/api/metrics")
        assert response.status_code == 200
        data = response.json()
        assert "total_requests" in data
        assert "avg_response_ms" in data
        assert "p95_response_ms" in data
        assert "p99_response_ms" in data
        assert "error_rate" in data

    async def test_metrics_count_increases(self, client: AsyncClient) -> None:
        await client.get("/api/metrics")
        response = await client.get("/api/metrics")
        data = response.json()
        assert data["total_requests"] >= 2


class TestMetricsMiddleware:
    async def test_response_time_header(self, client: AsyncClient) -> None:
        response = await client.get("/health")
        assert "X-Response-Time" in response.headers
        assert response.headers["X-Response-Time"].endswith("ms")


class TestCacheClearEndpoint:
    async def test_cache_clear(self, client: AsyncClient) -> None:
        response = await client.post("/api/metrics/cache/clear")
        assert response.status_code == 200
        assert response.json()["status"] == "cache cleared"


class TestMetricsUnit:
    def test_get_metrics_returns_dict(self) -> None:
        metrics = get_metrics()
        assert isinstance(metrics, dict)
        assert "total_requests" in metrics
        assert "error_rate" in metrics
