from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import loguru
from fastapi import FastAPI

from backend.app.services.database import close_db, init_db
from backend.app.services.logging import RequestIDMiddleware, setup_logging


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    setup_logging()
    loguru.logger.info("Application starting up")
    await init_db()
    loguru.logger.info("Application startup complete")
    yield
    loguru.logger.info("Application shutting down")
    await close_db()


app = FastAPI(
    title="AI Task Manager",
    description="Local-first AI task management assistant",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(RequestIDMiddleware)


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}
