from __future__ import annotations

import asyncio
import uuid
from unittest.mock import AsyncMock, MagicMock

from backend.app.agents.email_draft_agent import DraftEmail
from backend.app.services.queues.missing_info_queue import MissingInfoQueue


class TestMissingInfoQueue:
    def _make_draft(self, ticket_id: str | None = None, conversation_id: str | None = None) -> DraftEmail:
        return DraftEmail(
            to="bob@example.com",
            subject="Re: Website redesign",
            body="Please provide missing info",
            missing_fields=["project_number"],
            ticket_id=uuid.UUID(ticket_id or "550e8400-e29b-41d4-a716-446655440000"),
            conversation_id=conversation_id,
        )

    def test_add_to_queue(self) -> None:
        queue = MissingInfoQueue()
        draft = self._make_draft()
        item = asyncio.run(
            queue.add_to_queue("550e8400-e29b-41d4-a716-446655440000", draft, ["project_number"])
        )
        assert item.status == "PENDING"
        assert item.missing_fields == ["project_number"]

    def test_get_queue(self) -> None:
        queue = MissingInfoQueue()
        draft = self._make_draft()
        asyncio.run(queue.add_to_queue("550e8400-e29b-41d4-a716-446655440000", draft, ["project_number"]))
        items = asyncio.run(queue.get_queue())
        assert len(items) == 1

    def test_approve_item(self) -> None:
        queue = MissingInfoQueue()
        draft = self._make_draft()
        asyncio.run(queue.add_to_queue("550e8400-e29b-41d4-a716-446655440000", draft, ["project_number"]))
        item = asyncio.run(queue.approve_item("550e8400-e29b-41d4-a716-446655440000"))
        assert item is not None
        assert item.status == "APPROVED"

    def test_approve_item_sends_email_sets_awaiting_reply(self) -> None:
        queue = MissingInfoQueue()
        draft = self._make_draft(conversation_id="conv-789")
        asyncio.run(queue.add_to_queue("550e8400-e29b-41d4-a716-446655440000", draft, ["project_number"]))

        mock_email_provider = MagicMock()
        mock_email_provider.send_new_email = AsyncMock()

        item = asyncio.run(
            queue.approve_item(
                "550e8400-e29b-41d4-a716-446655440000",
                email_provider=mock_email_provider,
            )
        )
        assert item is not None
        assert item.status == "AWAITING_REPLY"
        mock_email_provider.send_new_email.assert_awaited_once_with(
            to="bob@example.com",
            subject="Re: Website redesign",
            body="Please provide missing info",
            conversation_id="conv-789",
        )

    def test_approve_item_email_failure_resets_to_pending(self) -> None:
        queue = MissingInfoQueue()
        draft = self._make_draft()
        asyncio.run(queue.add_to_queue("550e8400-e29b-41d4-a716-446655440000", draft, ["project_number"]))

        mock_email_provider = MagicMock()
        mock_email_provider.send_new_email = AsyncMock(side_effect=Exception("Outlook down"))

        item = asyncio.run(
            queue.approve_item(
                "550e8400-e29b-41d4-a716-446655440000",
                email_provider=mock_email_provider,
            )
        )
        assert item is not None
        assert item.status == "PENDING"

    def test_reject_item(self) -> None:
        queue = MissingInfoQueue()
        draft = self._make_draft()
        asyncio.run(queue.add_to_queue("550e8400-e29b-41d4-a716-446655440000", draft, ["project_number"]))
        item = asyncio.run(queue.reject_item("550e8400-e29b-41d4-a716-446655440000", reason="Not needed"))
        assert item is not None
        assert item.status == "REJECTED"

    def test_update_draft(self) -> None:
        queue = MissingInfoQueue()
        draft = self._make_draft()
        asyncio.run(queue.add_to_queue("550e8400-e29b-41d4-a716-446655440000", draft, ["project_number"]))
        new_draft = self._make_draft()
        new_draft.body = "Updated draft body"
        item = asyncio.run(queue.update_draft("550e8400-e29b-41d4-a716-446655440000", new_draft))
        assert item is not None
        assert item.draft_email.body == "Updated draft body"

    def test_get_item_not_found(self) -> None:
        queue = MissingInfoQueue()
        item = asyncio.run(queue.get_item("00000000-0000-0000-0000-000000000001"))
        assert item is None

    def test_conversation_id_round_trip(self) -> None:
        queue = MissingInfoQueue()
        draft = self._make_draft(conversation_id="conv-abc")
        asyncio.run(queue.add_to_queue("550e8400-e29b-41d4-a716-446655440000", draft, ["project_number"]))
        items = asyncio.run(queue.get_queue())
        assert len(items) == 1
        assert items[0].draft_email.conversation_id == "conv-abc"

    def test_conversation_id_none_round_trip(self) -> None:
        queue = MissingInfoQueue()
        draft = self._make_draft(conversation_id=None)
        asyncio.run(queue.add_to_queue("550e8400-e29b-41d4-a716-446655440000", draft, ["project_number"]))
        items = asyncio.run(queue.get_queue())
        assert len(items) == 1
        assert items[0].draft_email.conversation_id is None

    def test_approve_item_edits_preserve_conversation_id(self) -> None:
        queue = MissingInfoQueue()
        draft = self._make_draft(conversation_id="conv-orig")
        asyncio.run(queue.add_to_queue("550e8400-e29b-41d4-a716-446655440000", draft, ["project_number"]))

        edits = DraftEmail(
            to="alice@example.com",
            subject="Re: Updated subject",
            body="Updated body",
            missing_fields=["project_number"],
            ticket_id=uuid.UUID("550e8400-e29b-41d4-a716-446655440000"),
            conversation_id="conv-edited",
        )
        item = asyncio.run(
            queue.approve_item(
                "550e8400-e29b-41d4-a716-446655440000",
                edits=edits,
            )
        )
        assert item is not None
        assert item.draft_email.conversation_id == "conv-edited"

    def test_update_draft_preserves_conversation_id(self) -> None:
        queue = MissingInfoQueue()
        draft = self._make_draft(conversation_id="conv-upd")
        asyncio.run(queue.add_to_queue("550e8400-e29b-41d4-a716-446655440000", draft, ["project_number"]))

        new_draft = DraftEmail(
            to="bob@example.com",
            subject="Re: Website redesign",
            body="Updated body",
            missing_fields=["project_number"],
            ticket_id=uuid.UUID("550e8400-e29b-41d4-a716-446655440000"),
            conversation_id="conv-upd",
        )
        item = asyncio.run(queue.update_draft("550e8400-e29b-41d4-a716-446655440000", new_draft))
        assert item is not None
        assert item.draft_email.conversation_id == "conv-upd"
