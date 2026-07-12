from __future__ import annotations

import asyncio
from datetime import datetime

from backend.app.agents.calendar_planning_agent import ScheduleBlock, ScheduleSuggestion
from backend.app.services.queues.scheduling_queue import SchedulingQueue


class TestSchedulingQueue:
    def _make_suggestion(self) -> ScheduleSuggestion:
        now = datetime.now()
        return ScheduleSuggestion(
            blocks=[
                ScheduleBlock(
                    start_time=now.replace(hour=9, minute=0),
                    end_time=now.replace(hour=13, minute=0),
                    hours=4.0,
                    description="Morning work block",
                )
            ],
            total_hours=4.0,
            fits_deadline=True,
            confidence=0.8,
        )

    def test_add_to_queue(self) -> None:
        queue = SchedulingQueue()
        suggestion = self._make_suggestion()
        item = asyncio.run(
            queue.add_to_queue("550e8400-e29b-41d4-a716-446655440000", suggestion)
        )
        assert item.status == "PENDING"
        assert item.suggestion.total_hours == 4.0

    def test_get_queue(self) -> None:
        queue = SchedulingQueue()
        suggestion = self._make_suggestion()
        asyncio.run(queue.add_to_queue("550e8400-e29b-41d4-a716-446655440000", suggestion))
        items = asyncio.run(queue.get_queue())
        assert len(items) == 1

    def test_approve_schedule(self) -> None:
        queue = SchedulingQueue()
        suggestion = self._make_suggestion()
        asyncio.run(queue.add_to_queue("550e8400-e29b-41d4-a716-446655440000", suggestion))
        item = asyncio.run(queue.approve_schedule("550e8400-e29b-41d4-a716-446655440000"))
        assert item is not None
        assert item.status == "APPROVED"

    def test_decline_schedule(self) -> None:
        queue = SchedulingQueue()
        suggestion = self._make_suggestion()
        asyncio.run(queue.add_to_queue("550e8400-e29b-41d4-a716-446655440000", suggestion))
        item = asyncio.run(queue.decline_schedule("550e8400-e29b-41d4-a716-446655440000", reason="Too expensive"))
        assert item is not None
        assert item.status == "DECLINED"

    def test_modify_schedule(self) -> None:
        queue = SchedulingQueue()
        suggestion = self._make_suggestion()
        asyncio.run(queue.add_to_queue("550e8400-e29b-41d4-a716-446655440000", suggestion))
        now = datetime.now()
        new_blocks = [
            ScheduleBlock(
                start_time=now.replace(hour=14, minute=0),
                end_time=now.replace(hour=18, minute=0),
                hours=4.0,
                description="Afternoon work block",
            )
        ]
        item = asyncio.run(queue.modify_schedule("550e8400-e29b-41d4-a716-446655440000", new_blocks))
        assert item is not None
        assert item.suggestion.blocks[0].description == "Afternoon work block"
