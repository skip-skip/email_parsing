from __future__ import annotations

import os

import loguru
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from backend.app.services.database import async_session_factory
from backend.app.services.database.repositories.email_repository import EmailRepository
from backend.app.services.email_processor import EmailProcessor
from backend.app.services.outlook.base import EmailProvider


def _get_poll_interval() -> int:
    return int(os.environ.get("POLL_INTERVAL_SECONDS", "30"))


def _is_outlook_enabled() -> bool:
    return os.environ.get("OUTLOOK_ENABLED", "true").lower() == "true"


class OutlookMonitor:
    """Background service that polls the Outlook inbox for new emails.

    Uses APScheduler to run periodic polls. New emails are detected by
    their EntryID and stored in the database. Polling can be disabled
    via the OUTLOOK_ENABLED environment variable.
    """

    def __init__(self, email_provider: EmailProvider) -> None:
        """Initialize the monitor with an email provider implementation.

        Args:
            email_provider: Provider used to retrieve messages from Outlook.
        """
        self._email_provider = email_provider
        self._scheduler = AsyncIOScheduler()
        self._last_poll_count = 0
        self._processor = EmailProcessor()

    async def _poll_async(self) -> None:
        try:
            messages = await self._email_provider.get_new_messages()
            new_count = 0
            new_messages: list = []
            seen_entry_ids: set[str] = set()
            async with async_session_factory() as session:
                email_repo = EmailRepository(session)
                for msg in messages:
                    if msg.entry_id in seen_entry_ids:
                        continue
                    seen_entry_ids.add(msg.entry_id)
                    existing = await email_repo.get_by_entry_id(msg.entry_id)
                    if existing is None:
                        await email_repo.create(
                            conversation_id=msg.conversation_id,
                            entry_id=msg.entry_id,
                            sender=msg.sender,
                            subject=msg.subject,
                            body=msg.body,
                            received_time=msg.received_time,
                            attachments=msg.attachments,
                        )
                        new_messages.append(msg)
                        new_count += 1
                    if new_count % 10 == 0 and new_count > 0:
                        await session.commit()
                await session.commit()

            for msg in new_messages:
                try:
                    result = await self._processor.process_new_email(msg)
                    if result.is_task:
                        loguru.logger.info(
                            "Processed task email {} -> ticket {} (workflow: {})",
                            msg.entry_id,
                            result.ticket_id,
                            result.workflow_status,
                        )
                    else:
                        loguru.logger.debug(
                            "Email {} classified as non-task ({})",
                            msg.entry_id,
                            result.classification.category if result.classification else "unknown",
                        )
                except Exception:
                    loguru.logger.exception(
                        "Error processing email {} through pipeline", msg.entry_id
                    )

            self._last_poll_count = new_count
            if new_count > 0:
                loguru.logger.info("Detected {} new emails", new_count)
        except Exception:
            loguru.logger.exception("Error polling Outlook")

    def start(self) -> None:
        """Start the background polling scheduler.

        Reads the poll interval from POLL_INTERVAL_SECONDS (default: 30).
        Does nothing if OUTLOOK_ENABLED is set to 'false'.
        """
        if not _is_outlook_enabled():
            loguru.logger.info("Outlook monitor disabled via OUTLOOK_ENABLED=false")
            return
        poll_interval = _get_poll_interval()
        trigger = IntervalTrigger(seconds=poll_interval)
        self._scheduler.add_job(
            self._poll_async,
            trigger,
            id="outlook_poll",
            max_instances=1,
            misfire_grace_time=max(1, poll_interval // 2),
            replace_existing=True,
        )
        self._scheduler.start()
        loguru.logger.info(
            "Outlook monitor started (polling every {}s)", poll_interval
        )

    def stop(self) -> None:
        """Stop the background polling scheduler."""
        if self._scheduler.running:
            self._scheduler.shutdown(wait=False)
            loguru.logger.info("Outlook monitor stopped")
