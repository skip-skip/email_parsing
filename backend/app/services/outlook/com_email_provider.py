from __future__ import annotations

import asyncio
import logging
import tempfile
import time
from pathlib import Path

from backend.app.services.outlook.base import EmailProvider
from backend.app.services.outlook.models import EmailMessage

logger = logging.getLogger(__name__)

MAX_RETRIES = 3
RETRY_DELAY = 1.0


def _get_outlook_application():
    import pythoncom

    pythoncom.CoInitialize()
    import win32com.client

    return win32com.client.Dispatch("Outlook.Application")


def _get_namespace(app):
    return app.GetNamespace("MAPI")


def _get_inbox(namespace):
    return namespace.GetDefaultFolder(6)


def _map_com_message(message) -> EmailMessage:
    attachments = []
    for i in range(1, message.Attachments.Count + 1):
        try:
            attachment = message.Attachments.Item(i)
            temp_dir = Path(tempfile.gettempdir()) / "outlook_attachments"
            temp_dir.mkdir(exist_ok=True)
            file_path = temp_dir / attachment.FileName
            attachment.SaveAsFile(str(file_path))
            attachments.append(str(file_path))
        except Exception:
            logger.warning("Failed to save attachment: %s", getattr(attachment, "FileName", "unknown"))

    return EmailMessage(
        conversation_id=message.ConversationID or "",
        entry_id=message.EntryID or "",
        sender=message.SenderName or "",
        subject=message.Subject or "",
        body=message.Body or "",
        received_time=message.ReceivedTime,
        attachments=attachments,
    )


class OutlookComEmailProvider(EmailProvider):
    def __init__(self) -> None:
        self._app = None
        self._namespace = None

    def _connect(self) -> None:
        self._app = _get_outlook_application()
        self._namespace = _get_namespace(self._app)

    def _connect_with_retry(self) -> None:
        last_error: Exception | None = None
        for attempt in range(MAX_RETRIES):
            try:
                self._connect()
                return
            except Exception as e:
                last_error = e
                logger.warning(
                    "Outlook connection attempt %d/%d failed: %s",
                    attempt + 1,
                    MAX_RETRIES,
                    e,
                )
                if attempt < MAX_RETRIES - 1:
                    time.sleep(RETRY_DELAY * (attempt + 1))
        raise ConnectionError(
            f"Failed to connect to Outlook after {MAX_RETRIES} attempts"
        ) from last_error

    def _fetch_messages(self) -> list[EmailMessage]:
        inbox = _get_inbox(self._namespace)
        messages = inbox.Items
        unread = messages.Restrict("[UnRead] = True")
        unread.Sort("[ReceivedTime]", True)
        return [_map_com_message(msg) for msg in unread]

    def _fetch_conversation(self, conversation_id: str) -> list[EmailMessage]:
        inbox = _get_inbox(self._namespace)
        messages = inbox.Items
        filter_str = f"[ConversationID] = '{conversation_id}'"
        conversation = messages.Restrict(filter_str)
        conversation.Sort("[ReceivedTime]")
        return [_map_com_message(msg) for msg in conversation]

    def _send_reply(self, conversation_id: str, body: str) -> None:
        inbox = _get_inbox(self._namespace)
        messages = inbox.Items
        filter_str = f"[ConversationID] = '{conversation_id}'"
        conversation = messages.Restrict(filter_str)
        conversation.Sort("[ReceivedTime]", True)
        original = conversation.items[0]
        reply = original.Reply()
        reply.Body = body
        reply.Send()

    def _get_message_by_entry_id(self, entry_id: str) -> EmailMessage | None:
        try:
            message = self._namespace.GetItemFromID(entry_id)
            return _map_com_message(message)
        except Exception:
            return None

    async def get_new_messages(self) -> list[EmailMessage]:
        def _fetch():
            self._connect_with_retry()
            return self._fetch_messages()

        return await asyncio.to_thread(_fetch)

    async def get_conversation(self, conversation_id: str) -> list[EmailMessage]:
        def _fetch():
            self._connect_with_retry()
            return self._fetch_conversation(conversation_id)

        return await asyncio.to_thread(_fetch)

    async def send_reply(self, conversation_id: str, body: str) -> None:
        def _send():
            self._connect_with_retry()
            self._send_reply(conversation_id, body)

        await asyncio.to_thread(_send)

    async def get_message_by_entry_id(self, entry_id: str) -> EmailMessage | None:
        def _fetch():
            self._connect_with_retry()
            return self._get_message_by_entry_id(entry_id)

        return await asyncio.to_thread(_fetch)
