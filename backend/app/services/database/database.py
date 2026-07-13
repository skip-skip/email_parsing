import os
from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from backend.app.services.database.base import Base

DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite+aiosqlite:///./data.db")

# SQLite does not support pool_size / max_overflow; only configure for PostgreSQL.
_pool_kwargs: dict[str, object] = {}
if DATABASE_URL.startswith("postgresql"):
    _pool_kwargs = {
        "pool_size": int(os.environ.get("DB_POOL_SIZE", "10")),
        "max_overflow": int(os.environ.get("DB_MAX_OVERFLOW", "20")),
        "pool_timeout": int(os.environ.get("DB_POOL_TIMEOUT", "30")),
        "pool_recycle": int(os.environ.get("DB_POOL_RECYCLE", "1800")),
        "pool_pre_ping": True,
    }

engine = create_async_engine(DATABASE_URL, echo=False, **_pool_kwargs)

async_session_factory = async_sessionmaker(engine, expire_on_commit=False)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency that yields a database session.

    The session is automatically closed after the request completes.
    """
    async with async_session_factory() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db() -> None:
    """Create all database tables defined by SQLAlchemy models."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_db() -> None:
    """Dispose of the database engine and release connections."""
    await engine.dispose()
