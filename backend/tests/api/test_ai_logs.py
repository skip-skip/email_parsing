from __future__ import annotations

import uuid
from collections.abc import AsyncGenerator

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from backend.app.main import app
from backend.app.services.database import get_db
from backend.app.services.database.base import Base
from backend.app.services.database.repositories.ai_log_repository import AILogRepository


@pytest.fixture
async def db_setup() -> AsyncGenerator[
    tuple[async_sessionmaker[AsyncSession], AsyncClient],
    None,
]:
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
        yield session_factory, ac

    app.dependency_overrides.clear()
    await engine.dispose()


class TestAILogAPI:
    async def test_list_logs_empty(self, db_setup: tuple) -> None:
        _, client = db_setup
        response = await client.get("/api/ai-logs")
        assert response.status_code == 200
        data = response.json()
        assert data["items"] == []
        assert data["total"] == 0

    async def test_list_logs_with_data(self, db_setup: tuple) -> None:
        session_factory, client = db_setup
        async with session_factory() as session:
            repo = AILogRepository(session)
            for i in range(3):
                await repo.create(
                    model="qwen3:8b",
                    prompt_version="v1",
                    prompt=f"prompt {i}",
                    response=f"response {i}",
                )
            await session.commit()

        response = await client.get("/api/ai-logs")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 3
        assert len(data["items"]) == 3

    async def test_get_logs_by_ticket(self, db_setup: tuple) -> None:
        _, client = db_setup
        ticket_id = str(uuid.uuid4())
        response = await client.get(f"/api/ai-logs/{ticket_id}")
        assert response.status_code == 200
        assert response.json() == []

    async def test_get_stats(self, db_setup: tuple) -> None:
        _, client = db_setup
        response = await client.get("/api/ai-logs/stats")
        assert response.status_code == 200
        data = response.json()
        assert data["total_interactions"] == 0
        assert data["success_rate"] == 0.0

    async def test_list_logs_pagination(self, db_setup: tuple) -> None:
        _, client = db_setup
        response = await client.get("/api/ai-logs?offset=0&limit=2")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert "offset" in data
        assert "limit" in data

    async def test_filter_by_model(self, db_setup: tuple) -> None:
        session_factory, client = db_setup
        async with session_factory() as session:
            repo = AILogRepository(session)
            await repo.create(
                model="qwen3:8b", prompt_version="v1", prompt="p1", response="r1"
            )
            await repo.create(
                model="gemma3:12b", prompt_version="v1", prompt="p2", response="r2"
            )
            await session.commit()

        response = await client.get("/api/ai-logs?model=qwen3:8b")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["items"][0]["model"] == "qwen3:8b"

    async def test_filter_by_success(self, db_setup: tuple) -> None:
        session_factory, client = db_setup
        async with session_factory() as session:
            repo = AILogRepository(session)
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
            await session.commit()

        response = await client.get("/api/ai-logs?success=false")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["items"][0]["success"] is False

    async def test_stats_with_data(self, db_setup: tuple) -> None:
        session_factory, client = db_setup
        async with session_factory() as session:
            repo = AILogRepository(session)
            await repo.create(
                model="qwen3:8b",
                prompt_version="v1",
                prompt="p1",
                response="r1",
                success=True,
                execution_time_ms=100,
                input_tokens=50,
                output_tokens=25,
            )
            await session.commit()

        response = await client.get("/api/ai-logs/stats")
        assert response.status_code == 200
        data = response.json()
        assert data["total_interactions"] == 1
        assert data["successful_interactions"] == 1
        assert data["total_input_tokens"] == 50
        assert data["total_output_tokens"] == 25
