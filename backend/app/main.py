from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import loguru
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import FastAPI

from backend.app.api.ai_logs import router as ai_logs_router
from backend.app.api.error_handlers import register_error_handlers
from backend.app.api.llm import get_model_manager
from backend.app.api.llm import router as llm_router
from backend.app.api.logs import router as logs_router
from backend.app.api.queues import router as queues_router
from backend.app.api.scheduling import router as scheduling_router
from backend.app.api.tickets import router as tickets_router
from backend.app.services.database import close_db, init_db
from backend.app.services.logging import RequestIDMiddleware, setup_logging
from backend.app.services.outlook.com_email_provider import OutlookComEmailProvider
from backend.app.services.outlook.monitor import OutlookMonitor

_scheduler: AsyncIOScheduler | None = None


def _health_check_job() -> None:
    manager = get_model_manager()
    if manager.needs_health_check():
        manager.check_health()
        loguru.logger.debug("LLM health check completed")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    global _scheduler
    setup_logging()
    loguru.logger.info("Application starting up")
    await init_db()
    monitor = OutlookMonitor(OutlookComEmailProvider())
    monitor.start()
    _scheduler = AsyncIOScheduler()
    _scheduler.add_job(_health_check_job, "interval", minutes=5)
    _scheduler.start()
    manager = get_model_manager()
    manager.check_health()
    loguru.logger.info("Application startup complete")
    yield
    loguru.logger.info("Application shutting down")
    if _scheduler is not None:
        _scheduler.shutdown(wait=False)
    monitor.stop()
    await close_db()


app = FastAPI(
    title="AI Task Manager",
    description="Local-first AI task management assistant",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(RequestIDMiddleware)
register_error_handlers(app)
app.include_router(queues_router)
app.include_router(scheduling_router)
app.include_router(ai_logs_router)
app.include_router(llm_router)
app.include_router(tickets_router)
app.include_router(logs_router)


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}
