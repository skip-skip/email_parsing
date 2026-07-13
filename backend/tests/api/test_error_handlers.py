from __future__ import annotations

from collections.abc import AsyncGenerator

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from backend.app.main import app
from backend.app.services.database import get_db
from backend.app.services.database.base import Base
from backend.app.services.errors import (
    AppError,
    AuthenticationError,
    ConflictError,
    ExternalServiceError,
    NotFoundError,
    PermissionError,
    RateLimitError,
    TransientError,
    ValidationError,
    retry,
)


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


class TestErrorFormat:
    async def test_health_check_returns_ok(self, client: AsyncClient) -> None:
        response = await client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"

    async def test_not_found_route_returns_consistent_format(
        self, client: AsyncClient
    ) -> None:
        response = await client.get("/api/nonexistent")
        assert response.status_code == 404
        data = response.json()
        assert "error" in data
        assert "code" in data["error"]
        assert "message" in data["error"]

    async def test_ticket_not_found_returns_404(self, client: AsyncClient) -> None:
        response = await client.get(
            "/api/tickets/00000000-0000-0000-0000-000000000000"
        )
        assert response.status_code == 404
        data = response.json()
        assert data["error"]["code"] == 404
        assert "not found" in data["error"]["message"].lower()

    async def test_validation_error_returns_422(self, client: AsyncClient) -> None:
        response = await client.post(
            "/api/queues/missing-info/00000000-0000-0000-0000-000000000000/approve",
            json={"edits": "not-a-valid-object"},
        )
        assert response.status_code == 422
        data = response.json()
        assert data["error"]["code"] == 422
        assert "detail" in data["error"]


class TestCustomExceptions:
    def test_not_found_error_status(self) -> None:
        exc = NotFoundError("Widget not found")
        assert exc.status_code == 404
        assert exc.message == "Widget not found"

    def test_validation_error_status(self) -> None:
        exc = ValidationError("Bad input")
        assert exc.status_code == 422
        assert exc.message == "Bad input"

    def test_conflict_error_status(self) -> None:
        exc = ConflictError()
        assert exc.status_code == 409
        assert exc.message == "Resource conflict"

    def test_auth_error_status(self) -> None:
        exc = AuthenticationError()
        assert exc.status_code == 401

    def test_permission_error_status(self) -> None:
        exc = PermissionError()
        assert exc.status_code == 403

    def test_external_service_error_status(self) -> None:
        exc = ExternalServiceError("Ollama timeout")
        assert exc.status_code == 502

    def test_transient_error_status(self) -> None:
        exc = TransientError()
        assert exc.status_code == 503

    def test_rate_limit_error_status(self) -> None:
        exc = RateLimitError()
        assert exc.status_code == 429

    def test_base_app_error_defaults(self) -> None:
        exc = AppError()
        assert exc.status_code == 500
        assert exc.message == "An unexpected error occurred"
        assert exc.detail is None

    def test_error_with_detail(self) -> None:
        exc = NotFoundError("Not found", detail={"id": "abc"})
        assert exc.detail == {"id": "abc"}

    def test_error_is_exception(self) -> None:
        exc = AppError("test")
        assert isinstance(exc, Exception)


class TestRetryDecorator:
    async def test_retry_succeeds_on_first_try(self) -> None:
        call_count = 0

        @retry(max_retries=3, delay=0.01)
        async def success() -> str:
            nonlocal call_count
            call_count += 1
            return "ok"

        result = await success()
        assert result == "ok"
        assert call_count == 1

    async def test_retry_succeeds_after_failures(self) -> None:
        call_count = 0

        @retry(max_retries=3, delay=0.01, exceptions=(TransientError,))
        async def flaky() -> str:
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise TransientError("temporary")
            return "ok"

        result = await flaky()
        assert result == "ok"
        assert call_count == 3

    async def test_retry_exhausts_attempts(self) -> None:
        call_count = 0

        @retry(max_retries=2, delay=0.01, exceptions=(TransientError,))
        async def always_fails() -> None:
            nonlocal call_count
            call_count += 1
            raise TransientError("always failing")

        with pytest.raises(TransientError):
            await always_fails()
        assert call_count == 3  # 1 initial + 2 retries

    async def test_retry_does_not_catch_unrelated_exceptions(self) -> None:
        @retry(max_retries=3, delay=0.01, exceptions=(TransientError,))
        async def wrong_error() -> None:
            raise ValueError("not transient")

        with pytest.raises(ValueError, match="not transient"):
            await wrong_error()

    def test_sync_retry_succeeds(self) -> None:
        call_count = 0

        @retry(max_retries=3, delay=0.01, exceptions=(TransientError,))
        def sync_flaky() -> str:
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise TransientError("temporary")
            return "ok"

        result = sync_flaky()
        assert result == "ok"
        assert call_count == 2

    def test_sync_retry_exhausts(self) -> None:
        call_count = 0

        @retry(max_retries=2, delay=0.01, exceptions=(TransientError,))
        def sync_fails() -> None:
            nonlocal call_count
            call_count += 1
            raise TransientError("fail")

        with pytest.raises(TransientError):
            sync_fails()
        assert call_count == 3
