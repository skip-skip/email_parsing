from __future__ import annotations

import pytest
from unittest.mock import MagicMock, patch

from backend.app.services.outlook.com_email_provider import OutlookComEmailProvider
from backend.tests.outlook.mock_com import MockMailItem, MockOutlookApp


class TestOutlookComEmailProvider:
    @patch("backend.app.services.outlook.com_email_provider._get_outlook_application")
    def test_get_new_messages(self, mock_get_app: MagicMock) -> None:
        mock_app = MockOutlookApp()
        mock_get_app.return_value = mock_app

        unread = MockMailItem(UnRead=True, EntryID="unread-1")
        read = MockMailItem(UnRead=False, EntryID="read-1")
        mock_app._namespace._inbox.items.items = [unread, read]

        provider = OutlookComEmailProvider()
        provider._namespace = mock_app._namespace
        messages = provider._fetch_messages()

        assert len(messages) == 1
        assert messages[0].entry_id == "unread-1"
        assert messages[0].sender == "test@example.com"

    @patch("backend.app.services.outlook.com_email_provider._get_outlook_application")
    def test_get_conversation(self, mock_get_app: MagicMock) -> None:
        mock_app = MockOutlookApp()
        mock_get_app.return_value = mock_app

        msg1 = MockMailItem(ConversationID="conv-123", EntryID="e1")
        msg2 = MockMailItem(ConversationID="conv-123", EntryID="e2")
        msg3 = MockMailItem(ConversationID="other", EntryID="e3")
        mock_app._namespace._inbox.items.items = [msg1, msg2, msg3]

        provider = OutlookComEmailProvider()
        provider._namespace = mock_app._namespace
        messages = provider._fetch_conversation("conv-123")

        assert len(messages) == 2
        assert all(m.conversation_id == "conv-123" for m in messages)

    @patch("backend.app.services.outlook.com_email_provider._get_outlook_application")
    def test_send_reply(self, mock_get_app: MagicMock) -> None:
        mock_app = MockOutlookApp()
        mock_get_app.return_value = mock_app

        msg = MockMailItem(ConversationID="conv-123", EntryID="e1")
        mock_app._namespace._inbox.items.items = [msg]

        provider = OutlookComEmailProvider()
        provider._namespace = mock_app._namespace
        provider._send_reply("conv-123", "Reply body")

    @patch("backend.app.services.outlook.com_email_provider._get_outlook_application")
    def test_send_reply_all(self, mock_get_app: MagicMock) -> None:
        mock_app = MockOutlookApp()
        mock_get_app.return_value = mock_app

        msg1 = MockMailItem(ConversationID="conv-123", EntryID="e1")
        msg2 = MockMailItem(ConversationID="conv-123", EntryID="e2")
        mock_app._namespace._inbox.items.items = [msg1, msg2]

        provider = OutlookComEmailProvider()
        provider._namespace = mock_app._namespace
        provider._send_reply_all("conv-123", "Reply all body")

    @patch("backend.app.services.outlook.com_email_provider._get_outlook_application")
    def test_send_reply_empty_conversation_raises(self, mock_get_app: MagicMock) -> None:
        mock_app = MockOutlookApp()
        mock_get_app.return_value = mock_app
        mock_app._namespace._inbox.items.items = []

        provider = OutlookComEmailProvider()
        provider._namespace = mock_app._namespace
        with pytest.raises(ValueError, match="No emails found"):
            provider._send_reply("nonexistent-conv", "body")

    @patch("backend.app.services.outlook.com_email_provider._get_outlook_application")
    def test_send_reply_all_empty_conversation_raises(self, mock_get_app: MagicMock) -> None:
        mock_app = MockOutlookApp()
        mock_get_app.return_value = mock_app
        mock_app._namespace._inbox.items.items = []

        provider = OutlookComEmailProvider()
        provider._namespace = mock_app._namespace
        with pytest.raises(ValueError, match="No emails found"):
            provider._send_reply_all("nonexistent-conv", "body")

    @patch("backend.app.services.outlook.com_email_provider._get_outlook_application")
    def test_send_new_email(self, mock_get_app: MagicMock) -> None:
        mock_app = MockOutlookApp()
        mock_get_app.return_value = mock_app

        provider = OutlookComEmailProvider()
        provider._namespace = mock_app._namespace
        provider._send_new_email("bob@example.com", "Test Subject", "Hello Bob")

    @patch("backend.app.services.outlook.com_email_provider._get_outlook_application")
    def test_send_new_email_with_conversation(self, mock_get_app: MagicMock) -> None:
        mock_app = MockOutlookApp()
        mock_get_app.return_value = mock_app

        msg = MockMailItem(ConversationID="conv-456", EntryID="e1")
        mock_app._namespace._inbox.items.items = [msg]

        provider = OutlookComEmailProvider()
        provider._namespace = mock_app._namespace
        provider._send_new_email(
            "bob@example.com", "Re: Test", "Hello", conversation_id="conv-456"
        )

    @patch("backend.app.services.outlook.com_email_provider._get_outlook_application")
    def test_send_new_email_unknown_conversation_falls_back(self, mock_get_app: MagicMock) -> None:
        mock_app = MockOutlookApp()
        mock_get_app.return_value = mock_app
        mock_app._namespace._inbox.items.items = []

        provider = OutlookComEmailProvider()
        provider._namespace = mock_app._namespace
        provider._send_new_email(
            "bob@example.com", "Re: Test", "Hello", conversation_id="nonexistent"
        )

    @patch("backend.app.services.outlook.com_email_provider._get_outlook_application")
    def test_get_message_by_entry_id(self, mock_get_app: MagicMock) -> None:
        mock_app = MockOutlookApp()
        mock_get_app.return_value = mock_app

        msg = MockMailItem(EntryID="entry-001")
        mock_app._namespace._inbox.items.items = [msg]

        provider = OutlookComEmailProvider()
        provider._namespace = mock_app._namespace
        result = provider._get_message_by_entry_id("entry-001")

        assert result is not None
        assert result.entry_id == "entry-001"

    def test_get_message_by_entry_id_not_found(self) -> None:
        mock_app = MockOutlookApp()

        provider = OutlookComEmailProvider()
        provider._namespace = mock_app._namespace
        result = provider._get_message_by_entry_id("nonexistent")

        assert result is None

    @patch("backend.app.services.outlook.com_email_provider._get_outlook_application")
    def test_connection_retry(self, mock_get_app: MagicMock) -> None:
        mock_get_app.side_effect = [Exception("Connection failed"), MockOutlookApp()]

        provider = OutlookComEmailProvider()
        provider._connect_with_retry()

        assert mock_get_app.call_count == 2
