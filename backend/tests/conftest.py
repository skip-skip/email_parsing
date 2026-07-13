from __future__ import annotations

import asyncio
from collections.abc import AsyncGenerator

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from backend.app.services.database import async_session_factory
from backend.app.services.database.base import Base


@pytest.fixture(scope="session")
def event_loop() -> asyncio.AbstractEventLoop:
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    async with session_factory() as session:
        yield session

    await engine.dispose()


@pytest.fixture(autouse=True)
def _clean_queue_tables() -> None:
    """Truncate queue tables before each test to isolate DB-backed tests."""

    async def _truncate() -> None:
        async with async_session_factory() as session:
            await session.execute(text("DELETE FROM missing_info_queue"))
            await session.execute(text("DELETE FROM scheduling_queue"))
            await session.commit()

    asyncio.run(_truncate())
