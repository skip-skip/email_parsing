from __future__ import annotations

import asyncio
import uuid
from unittest.mock import MagicMock

import pytest

from backend.app.agents.email_draft_agent import DraftEmail
from backend.app.services.queues.missing_info_queue import MissingInfoQueue


class TestMissingInfoQueue:
    def _make_draft(self, ticket_id: str | None = None) -> DraftEmail:
        return DraftEmail(
            to="bob@example.com",
            subject="Re: Website redesign",
            body="Please provide missing info",
            missing_fields=["project_number"],
            ticket_id=uuid.UUID(ticket_id or "550e8400-e29b-41d4-a716-446655440000"),
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
