from __future__ import annotations

import uuid
from collections.abc import AsyncGenerator

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from backend.app.main import app
from backend.app.models.ticket import Ticket
from backend.app.services.database import get_db
from backend.app.services.database.base import Base


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

    # Seed some test tickets.
    async with session_factory() as session:
        for i in range(5):
            ticket = Ticket(
                ticket_id=uuid.uuid4(),
                status="ACCEPTED",
                client=f"Client {i}",
                contact=f"contact{i}@example.com",
                task_description=f"Task {i}",
                priority=i,
            )
            session.add(ticket)
        await session.commit()

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()
    await engine.dispose()


class TestTicketsPagination:
    async def test_returns_paginated_response(self, client: AsyncClient) -> None:
        response = await client.get("/api/tickets/active")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert "offset" in data
        assert "limit" in data
        assert data["total"] == 5
        assert data["offset"] == 0
        assert data["limit"] == 50

    async def test_pagination_offset_limit(self, client: AsyncClient) -> None:
        response = await client.get("/api/tickets/active?offset=2&limit=2")
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 2
        assert data["offset"] == 2
        assert data["limit"] == 2
        assert data["total"] == 5

    async def test_etag_header(self, client: AsyncClient) -> None:
        response = await client.get("/api/tickets/active")
        assert "etag" in response.headers

    async def test_etag_304(self, client: AsyncClient) -> None:
        response = await client.get("/api/tickets/active")
        etag = response.headers["etag"]
        response2 = await client.get(
            "/api/tickets/active",
            headers={"if-none-match": etag},
        )
        assert response2.status_code == 304


class TestTicketETag:
    async def test_single_ticket_etag(self, client: AsyncClient) -> None:
        list_response = await client.get("/api/tickets/active")
        first_ticket = list_response.json()["items"][0]
        ticket_id = first_ticket["ticket_id"]

        response = await client.get(f"/api/tickets/{ticket_id}")
        assert response.status_code == 200
        assert "etag" in response.headers

    async def test_single_ticket_304(self, client: AsyncClient) -> None:
        list_response = await client.get("/api/tickets/active")
        first_ticket = list_response.json()["items"][0]
        ticket_id = first_ticket["ticket_id"]

        response = await client.get(f"/api/tickets/{ticket_id}")
        etag = response.headers["etag"]
        response2 = await client.get(
            f"/api/tickets/{ticket_id}",
            headers={"if-none-match": etag},
        )
        assert response2.status_code == 304
