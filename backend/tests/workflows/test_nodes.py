from __future__ import annotations

from backend.app.workflows.nodes.receive_email import receive_email
from backend.app.workflows.nodes.draft_missing_info_email import draft_missing_info_email
from backend.app.workflows.nodes.plan_schedule import plan_schedule
from backend.app.workflows.nodes.create_calendar_event import create_calendar_event
from backend.app.workflows.nodes.dispatch_task import dispatch_task
from backend.app.workflows.nodes.route_by_validation import route_by_validation
from backend.app.workflows.states import WorkflowState


def _make_state(**overrides: object) -> WorkflowState:
    base: WorkflowState = {
        "ticket_id": "test-ticket",
        "status": "",
        "parsed_data": None,
        "validation_result": None,
        "missing_fields": [],
        "error": None,
    }
    base.update(overrides)  # type: ignore[arg-type]
    return base


class TestReceiveEmailNode:
    def test_sets_new_status(self) -> None:
        state = _make_state()
        result = receive_email(state)
        assert result["status"] == "NEW"


class TestDraftMissingInfoEmailNode:
    def test_sets_waiting_status(self) -> None:
        state = _make_state(missing_fields=["project_number", "deadline"])
        result = draft_missing_info_email(state)
        assert result["status"] == "WAITING_FOR_INFORMATION"
        assert "draft_email" in result
        assert "project_number" in result["draft_email"]


class TestPlanScheduleNode:
    def test_sets_ready_for_scheduling(self) -> None:
        state = _make_state(parsed_data={"deadline": "2025-12-31T00:00:00", "budget_hours": 40})
        result = plan_schedule(state)
        assert result["status"] == "READY_FOR_SCHEDULING"
        assert "schedule_blocks" in result


class TestCreateCalendarEventNode:
    def test_sets_calendar_created(self) -> None:
        state = _make_state()
        result = create_calendar_event(state)
        assert result["status"] == "CALENDAR_CREATED"
        assert "calendar_event_id" in result


class TestDispatchTaskNode:
    def test_sets_in_progress(self) -> None:
        state = _make_state()
        result = dispatch_task(state)
        assert result["status"] == "IN_PROGRESS"


class TestRouteByValidation:
    def test_routes_to_draft_when_missing(self) -> None:
        state = _make_state(missing_fields=["project_number"])
        result = route_by_validation(state)
        assert result == "draft_missing_info_email"

    def test_routes_to_schedule_when_complete(self) -> None:
        state = _make_state(missing_fields=[])
        result = route_by_validation(state)
        assert result == "plan_schedule"
