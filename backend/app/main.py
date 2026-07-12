from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import loguru
from fastapi import FastAPI

from backend.app.api.queues import router as queues_router
from backend.app.api.scheduling import router as scheduling_router
from backend.app.services.database import close_db, init_db
from backend.app.services.logging import RequestIDMiddleware, setup_logging
from backend.app.services.outlook.com_email_provider import OutlookComEmailProvider
from backend.app.services.outlook.monitor import OutlookMonitor


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    setup_logging()
    loguru.logger.info("Application starting up")
    await init_db()
    monitor = OutlookMonitor(OutlookComEmailProvider())
    monitor.start()
    loguru.logger.info("Application startup complete")
    yield
    loguru.logger.info("Application shutting down")
    monitor.stop()
    await close_db()


app = FastAPI(
    title="AI Task Manager",
    description="Local-first AI task management assistant",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(RequestIDMiddleware)
app.include_router(queues_router)
app.include_router(scheduling_router)


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}
