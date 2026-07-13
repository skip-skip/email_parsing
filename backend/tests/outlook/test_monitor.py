from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

from backend.app.services.outlook.base import EmailProvider
from backend.app.services.outlook.models import EmailMessage
from backend.app.services.outlook.monitor import OutlookMonitor


class MockEmailProvider(EmailProvider):
    def __init__(self) -> None:
        self.messages: list[EmailMessage] = []

    async def get_new_messages(self) -> list[EmailMessage]:
        return self.messages

    async def get_conversation(self, conversation_id: str) -> list[EmailMessage]:
        return [m for m in self.messages if m.conversation_id == conversation_id]

    async def send_reply(self, conversation_id: str, body: str) -> None:
        pass

    async def get_message_by_entry_id(self, entry_id: str) -> EmailMessage | None:
        for m in self.messages:
            if m.entry_id == entry_id:
                return m
        return None


class TestOutlookMonitor:
    def test_poll_calls_poll_async(self) -> None:
        mock_provider = MockEmailProvider()
        monitor = OutlookMonitor(mock_provider)
        monitor._poll_async = AsyncMock()
        asyncio.run(monitor._poll_async())
        monitor._poll_async.assert_called_once()

    @patch("backend.app.services.outlook.monitor._is_outlook_enabled", return_value=False)
    def test_start_disabled(self, mock_enabled: MagicMock) -> None:
        mock_provider = MockEmailProvider()
        monitor = OutlookMonitor(mock_provider)
        monitor.start()
        assert not monitor._scheduler.running

    @patch("backend.app.services.outlook.monitor._is_outlook_enabled", return_value=True)
    @patch("backend.app.services.outlook.monitor._get_poll_interval", return_value=1)
    def test_start_stop(self, mock_interval: MagicMock, mock_enabled: MagicMock) -> None:
        mock_provider = MockEmailProvider()
        monitor = OutlookMonitor(mock_provider)

        async def _run() -> None:
            monitor.start()
            assert monitor._scheduler.running
            monitor.stop()

        asyncio.run(_run())
        assert not monitor._scheduler.running

    @patch("backend.app.services.outlook.monitor.EmailRepository")
    @patch("backend.app.services.outlook.monitor.async_session_factory")
    @patch("backend.app.services.outlook.monitor.EmailProcessor")
    def test_new_email_triggers_processor(
        self,
        mock_processor_cls: MagicMock,
        mock_session_factory: MagicMock,
        mock_email_repo_cls: MagicMock,
    ) -> None:
        """New emails should be processed through the EmailProcessor pipeline."""
        from backend.app.agents.email_classification_agent import ClassificationResult

        mock_processor = MagicMock()
        mock_processor.process_new_email = AsyncMock(
            return_value=MagicMock(
                is_task=False,
                ticket_id=None,
                workflow_status=None,
                classification=ClassificationResult(
                    is_task=False,
                    category="newsletter",
                    confidence=0.9,
                    reason="Newsletter",
                ),
            )
        )
        mock_processor_cls.return_value = mock_processor

        mock_email_repo = MagicMock()
        mock_email_repo.get_by_entry_id = AsyncMock(return_value=None)
        mock_email_repo.create = AsyncMock()
        mock_email_repo_cls.return_value = mock_email_repo

        mock_session = AsyncMock()
        mock_session_factory.return_value.__aenter__.return_value = mock_session

        msg = EmailMessage(
            conversation_id="conv-1",
            entry_id="entry-1",
            sender="test@example.com",
            subject="Newsletter",
            body="Monthly update",
            received_time=None,
        )

        mock_provider = MockEmailProvider()
        mock_provider.messages = [msg]

        monitor = OutlookMonitor(mock_provider)
        asyncio.run(monitor._poll_async())

        mock_processor.process_new_email.assert_awaited_once_with(msg)

    @patch("backend.app.services.outlook.monitor.EmailRepository")
    @patch("backend.app.services.outlook.monitor.async_session_factory")
    @patch("backend.app.services.outlook.monitor.EmailProcessor")
    def test_processor_error_does_not_crash_poll(
        self,
        mock_processor_cls: MagicMock,
        mock_session_factory: MagicMock,
        mock_email_repo_cls: MagicMock,
    ) -> None:
        """Processor failures should be caught and logged, not crash the poll loop."""
        mock_processor = MagicMock()
        mock_processor.process_new_email = AsyncMock(
            side_effect=Exception("LLM unavailable")
        )
        mock_processor_cls.return_value = mock_processor

        mock_email_repo = MagicMock()
        mock_email_repo.get_by_entry_id = AsyncMock(return_value=None)
        mock_email_repo.create = AsyncMock()
        mock_email_repo_cls.return_value = mock_email_repo

        mock_session = AsyncMock()
        mock_session_factory.return_value.__aenter__.return_value = mock_session

        msg = EmailMessage(
            conversation_id="conv-2",
            entry_id="entry-2",
            sender="test@example.com",
            subject="Task request",
            body="Please do this",
            received_time=None,
        )

        mock_provider = MockEmailProvider()
        mock_provider.messages = [msg]

        monitor = OutlookMonitor(mock_provider)
        asyncio.run(monitor._poll_async())

        mock_processor.process_new_email.assert_awaited_once_with(msg)
        assert monitor._last_poll_count == 1

    @patch("backend.app.services.outlook.monitor.EmailRepository")
    @patch("backend.app.services.outlook.monitor.async_session_factory")
    @patch("backend.app.services.outlook.monitor.EmailProcessor")
    def test_duplicate_email_not_processed_twice(
        self,
        mock_processor_cls: MagicMock,
        mock_session_factory: MagicMock,
        mock_email_repo_cls: MagicMock,
    ) -> None:
        """Duplicate entry IDs in the same poll should only be processed once."""
        mock_processor = MagicMock()
        mock_processor.process_new_email = AsyncMock(
            return_value=MagicMock(
                is_task=False,
                ticket_id=None,
                workflow_status=None,
                classification=None,
            )
        )
        mock_processor_cls.return_value = mock_processor

        mock_email_repo = MagicMock()
        mock_email_repo.get_by_entry_id = AsyncMock(return_value=None)
        mock_email_repo.create = AsyncMock()
        mock_email_repo_cls.return_value = mock_email_repo

        mock_session = AsyncMock()
        mock_session_factory.return_value.__aenter__.return_value = mock_session

        msg = EmailMessage(
            conversation_id="conv-3",
            entry_id="entry-3",
            sender="test@example.com",
            subject="Duplicate",
            body="Same email twice",
            received_time=None,
        )

        mock_provider = MockEmailProvider()
        mock_provider.messages = [msg, msg]

        monitor = OutlookMonitor(mock_provider)
        asyncio.run(monitor._poll_async())

        mock_processor.process_new_email.assert_awaited_once_with(msg)
