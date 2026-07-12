from __future__ import annotations

from typing import Any, TypedDict

from langgraph.graph import END, StateGraph

from backend.app.workflows.states import TicketStatus


class WorkflowState(TypedDict):
    ticket_id: str
    status: str
    parsed_data: dict[str, Any] | None
    validation_result: dict[str, Any] | None
    missing_fields: list[str]
    error: str | None


def _receive_email(state: WorkflowState) -> dict[str, Any]:
    return {"status": TicketStatus.NEW.value}


def _extract_task(state: WorkflowState) -> dict[str, Any]:
    return {"status": TicketStatus.PARSED.value}


def _validate_fields(state: WorkflowState) -> dict[str, Any]:
    return {"status": TicketStatus.VALIDATED.value}


def _route_by_validation(state: WorkflowState) -> str:
    if state.get("missing_fields"):
        return "draft_missing_info_email"
    return "plan_schedule"


def _draft_missing_info_email(state: WorkflowState) -> dict[str, Any]:
    return {"status": TicketStatus.WAITING_FOR_INFORMATION.value}


def _plan_schedule(state: WorkflowState) -> dict[str, Any]:
    return {"status": TicketStatus.READY_FOR_SCHEDULING.value}


def _schedule_approval(state: WorkflowState) -> dict[str, Any]:
    return {"status": TicketStatus.PENDING_USER_APPROVAL.value}


def _create_calendar_event(state: WorkflowState) -> dict[str, Any]:
    return {"status": TicketStatus.CALENDAR_CREATED.value}


def _dispatch_task(state: WorkflowState) -> dict[str, Any]:
    return {"status": TicketStatus.IN_PROGRESS.value}


def build_workflow_graph() -> StateGraph:
    graph = StateGraph(WorkflowState)

    graph.add_node("receive_email", _receive_email)
    graph.add_node("extract_task", _extract_task)
    graph.add_node("validate_fields", _validate_fields)
    graph.add_node("draft_missing_info_email", _draft_missing_info_email)
    graph.add_node("plan_schedule", _plan_schedule)
    graph.add_node("schedule_approval", _schedule_approval)
    graph.add_node("create_calendar_event", _create_calendar_event)
    graph.add_node("dispatch_task", _dispatch_task)

    graph.set_entry_point("receive_email")
    graph.add_edge("receive_email", "extract_task")
    graph.add_edge("extract_task", "validate_fields")
    graph.add_conditional_edges(
        "validate_fields",
        _route_by_validation,
        {
            "draft_missing_info_email": "draft_missing_info_email",
            "plan_schedule": "plan_schedule",
        },
    )
    graph.add_edge("draft_missing_info_email", END)
    graph.add_edge("plan_schedule", "schedule_approval")
    graph.add_edge("schedule_approval", "create_calendar_event")
    graph.add_edge("create_calendar_event", "dispatch_task")
    graph.add_edge("dispatch_task", END)

    return graph


def compile_workflow() -> Any:
    graph = build_workflow_graph()
    return graph.compile()
