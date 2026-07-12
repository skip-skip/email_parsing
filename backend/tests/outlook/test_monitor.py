from __future__ import annotations

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

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
        monitor._poll()
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
        monitor.start()
        assert monitor._scheduler.running
        monitor.stop()
        assert not monitor._scheduler.running
