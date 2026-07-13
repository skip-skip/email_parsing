from __future__ import annotations

from datetime import datetime
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

from backend.app.agents.acceptance_email_agent import AcceptanceEmailAgent
from backend.app.agents.calendar_planning_agent import (
    ScheduleBlock,
    ScheduleSuggestion,
)
from backend.app.services.queues.scheduling_queue import SchedulingQueue
from backend.app.workflows.graph import compile_workflow
from backend.app.workflows.nodes.create_calendar_event import create_calendar_event
from backend.app.workflows.nodes.dispatch_task import dispatch_task
from backend.app.workflows.nodes.plan_schedule import plan_schedule
from backend.app.workflows.nodes.route_by_validation import route_by_validation
from backend.app.workflows.nodes.validate_fields import validate_fields
from backend.app.workflows.states import WorkflowState


def _make_state(**overrides: Any) -> WorkflowState:
    base: WorkflowState = {
        "ticket_id": "test-ticket",
        "status": "",
        "parsed_data": None,
        "validation_result": None,
        "missing_fields": [],
        "error": None,
    }
    for key, value in overrides.items():
        base[key] = value  # type: ignore[literal-required]
    return base


class TestSchedulingFlow:
    """Integration tests for the scheduling workflow path.

    Flow: validate_fields → plan_schedule → create_calendar_event
          → dispatch_task
    """

    @patch("backend.app.agents.email_parsing_agent.async_session_factory")
    @patch("backend.app.agents.email_parsing_agent.OllamaClient")
    def test_scheduling_path_end_to_end(
        self,
        mock_ollama_cls: MagicMock,
        mock_session_factory: MagicMock,
        complete_email_data: dict[str, Any],
        complete_parsed_data: dict[str, Any],
    ) -> None:
        mock_client = MagicMock()
        mock_client.generate.return_value = str(complete_parsed_data)
        mock_client._parse_json.return_value = complete_parsed_data
        mock_client._get_client.return_value = MagicMock()
        mock_ollama_cls.return_value = mock_client

        mock_session = AsyncMock()
        mock_session_factory.return_value.__aenter__.return_value = mock_session
        mock_session_factory.return_value.__aexit__ = AsyncMock(return_value=False)

        mock_log_repo = MagicMock()
        mock_log_repo.create = AsyncMock()

        with patch(
            "backend.app.agents.email_parsing_agent.AILogRepository",
            return_value=mock_log_repo,
        ):
            wf = compile_workflow()
            result = wf.invoke({
                "ticket_id": complete_email_data["ticket_id"],
                "status": "",
                "parsed_data": None,
                "validation_result": None,
                "missing_fields": [],
                "error": None,
                "sender": complete_email_data["sender"],
                "subject": complete_email_data["subject"],
                "body": complete_email_data["body"],
            })

        assert result["status"] == "IN_PROGRESS"

    @patch("backend.app.agents.email_parsing_agent.async_session_factory")
    @patch("backend.app.agents.email_parsing_agent.OllamaClient")
    def test_calendar_event_created_in_workflow(
        self,
        mock_ollama_cls: MagicMock,
        mock_session_factory: MagicMock,
        complete_email_data: dict[str, Any],
        complete_parsed_data: dict[str, Any],
    ) -> None:
        mock_client = MagicMock()
        mock_client.generate.return_value = str(complete_parsed_data)
        mock_client._parse_json.return_value = complete_parsed_data
        mock_client._get_client.return_value = MagicMock()
        mock_ollama_cls.return_value = mock_client

        mock_session = AsyncMock()
        mock_session_factory.return_value.__aenter__.return_value = mock_session
        mock_session_factory.return_value.__aexit__ = AsyncMock(return_value=False)

        mock_log_repo = MagicMock()
        mock_log_repo.create = AsyncMock()

        with patch(
            "backend.app.agents.email_parsing_agent.AILogRepository",
            return_value=mock_log_repo,
        ):
            wf = compile_workflow()
            result = wf.invoke({
                "ticket_id": complete_email_data["ticket_id"],
                "status": "",
                "parsed_data": None,
                "validation_result": None,
                "missing_fields": [],
                "error": None,
                "sender": complete_email_data["sender"],
                "subject": complete_email_data["subject"],
                "body": complete_email_data["body"],
            })

        assert result["status"] == "IN_PROGRESS"
        assert result["validation_result"]["is_valid"] is True

    def test_plan_schedule_node_creates_blocks(self) -> None:
        state = _make_state(
            parsed_data={
                "deadline": "2025-08-15T00:00:00",
                "budget_hours": 40.0,
            }
        )
        result = plan_schedule(state)
        assert result["status"] == "READY_FOR_SCHEDULING"
        assert "schedule_blocks" in result
        assert len(result["schedule_blocks"]) > 0

    def test_create_calendar_event_node(self) -> None:
        state = _make_state(ticket_id="test-ticket-123")
        result = create_calendar_event(state)
        assert result["status"] == "CALENDAR_CREATED"
        assert result["calendar_event_id"] == "evt-test-ticket-123"

    def test_dispatch_task_node(self) -> None:
        state = _make_state()
        result = dispatch_task(state)
        assert result["status"] == "IN_PROGRESS"

    def test_validation_to_schedule_routing(self) -> None:
        state = _make_state(missing_fields=[])
        result = route_by_validation(state)
        assert result == "plan_schedule"

    def test_validation_to_draft_routing(self) -> None:
        state = _make_state(missing_fields=["deadline"])
        result = route_by_validation(state)
        assert result == "draft_missing_info_email"

    def test_full_node_sequence_scheduling_path(self) -> None:
        state = _make_state(
            ticket_id="seq-test-1",
            parsed_data={
                "deadline": "2025-12-31T00:00:00",
                "budget_hours": 20.0,
                "project_number": "PRJ-001",
                "task_description": "Build new feature for client dashboard",
            },
        )

        validate_result = validate_fields(state)
        assert validate_result["validation_result"]["is_valid"] is True

        combined_state = _make_state(
            ticket_id="seq-test-1",
            parsed_data=state["parsed_data"],
            missing_fields=validate_result["missing_fields"],
        )
        route = route_by_validation(combined_state)
        assert route == "plan_schedule"

        schedule_result = plan_schedule(combined_state)
        assert schedule_result["status"] == "READY_FOR_SCHEDULING"

        cal_state = _make_state(
            ticket_id="seq-test-1",
            parsed_data=combined_state["parsed_data"],
            missing_fields=[],
        )
        cal_result = create_calendar_event(cal_state)
        assert cal_result["status"] == "CALENDAR_CREATED"

        dispatch_state = _make_state(
            ticket_id="seq-test-1",
            parsed_data=combined_state["parsed_data"],
            missing_fields=[],
        )
        dispatch_result = dispatch_task(dispatch_state)
        assert dispatch_result["status"] == "IN_PROGRESS"


class TestSchedulingQueueFlow:
    """Integration tests for the scheduling queue service."""

    def test_add_to_scheduling_queue(self) -> None:
        queue = SchedulingQueue()
        suggestion = ScheduleSuggestion(
            blocks=[
                ScheduleBlock(
                    start_time=datetime(2025, 8, 12, 9, 0),
                    end_time=datetime(2025, 8, 12, 13, 0),
                    hours=4.0,
                    description="Website redesign work",
                ),
            ],
            total_hours=4.0,
            fits_deadline=True,
            confidence=0.8,
        )

        async def _test() -> None:
            item = await queue.add_to_queue(
                ticket_id="550e8400-e29b-41d4-a716-446655440001",
                suggestion=suggestion,
            )
            assert item is not None
            assert item.status == "PENDING"

            items = await queue.get_queue()
            assert len(items) == 1

        import asyncio
        asyncio.run(_test())

    def test_approve_schedule(self) -> None:
        queue = SchedulingQueue()
        suggestion = ScheduleSuggestion(
            blocks=[
                ScheduleBlock(
                    start_time=datetime(2025, 8, 12, 9, 0),
                    end_time=datetime(2025, 8, 12, 13, 0),
                    hours=4.0,
                    description="Work block",
                ),
            ],
            total_hours=4.0,
            fits_deadline=True,
            confidence=0.8,
        )

        async def _test() -> None:
            await queue.add_to_queue(
                ticket_id="550e8400-e29b-41d4-a716-446655440001",
                suggestion=suggestion,
            )
            item = await queue.approve_schedule(
                ticket_id="550e8400-e29b-41d4-a716-446655440001",
            )
            assert item is not None
            assert item.status == "APPROVED"

            items = await queue.get_queue()
            assert len(items) == 0

        import asyncio
        asyncio.run(_test())

    def test_decline_schedule(self) -> None:
        queue = SchedulingQueue()
        suggestion = ScheduleSuggestion(
            blocks=[
                ScheduleBlock(
                    start_time=datetime(2025, 8, 12, 9, 0),
                    end_time=datetime(2025, 8, 12, 13, 0),
                    hours=4.0,
                    description="Work block",
                ),
            ],
            total_hours=4.0,
            fits_deadline=True,
            confidence=0.8,
        )

        async def _test() -> None:
            await queue.add_to_queue(
                ticket_id="550e8400-e29b-41d4-a716-446655440001",
                suggestion=suggestion,
            )
            item = await queue.decline_schedule(
                ticket_id="550e8400-e29b-41d4-a716-446655440001",
                reason="Too many hours",
            )
            assert item is not None
            assert item.status == "DECLINED"

        import asyncio
        asyncio.run(_test())


class TestAcceptanceEmailFlow:
    """Integration tests for the acceptance email agent."""

    def test_draft_acceptance_email(self) -> None:
        agent = AcceptanceEmailAgent()
        blocks = [
            ScheduleBlock(
                start_time=datetime(2025, 8, 12, 9, 0),
                end_time=datetime(2025, 8, 12, 13, 0),
                hours=4.0,
                description="Redesign website branding",
            ),
            ScheduleBlock(
                start_time=datetime(2025, 8, 13, 13, 0),
                end_time=datetime(2025, 8, 13, 17, 0),
                hours=4.0,
                description="Mobile responsive design",
            ),
        ]

        draft = agent.draft_acceptance(
            ticket_id="550e8400-e29b-41d4-a716-446655440001",
            client="Acme Corp",
            contact="Jane Smith",
            subject="Q3 Marketing Campaign",
            blocks=blocks,
            task_description="Redesign website",
        )

        assert draft.to == "Jane Smith"
        assert "Re: Q3 Marketing Campaign" in draft.subject
        assert "8.0" in draft.body
        assert "2025-08-12" in draft.body

    def test_draft_decline_email(self) -> None:
        agent = AcceptanceEmailAgent()
        draft = agent.draft_decline(
            ticket_id="550e8400-e29b-41d4-a716-446655440001",
            client="Acme Corp",
            contact="Jane Smith",
            subject="Q3 Marketing Campaign",
            reason="Overcommitted this quarter",
        )

        assert draft.to == "Jane Smith"
        assert "Re: Q3 Marketing Campaign" in draft.subject
        assert "Overcommitted" in draft.body
        assert draft.missing_fields == []
