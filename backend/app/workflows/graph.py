from __future__ import annotations

from typing import Any

from langgraph.graph import END, StateGraph

from backend.app.workflows.nodes.create_calendar_event import create_calendar_event
from backend.app.workflows.nodes.dispatch_task import dispatch_task
from backend.app.workflows.nodes.draft_missing_info_email import (
    draft_missing_info_email,
)
from backend.app.workflows.nodes.extract_task import extract_task
from backend.app.workflows.nodes.plan_schedule import plan_schedule
from backend.app.workflows.nodes.receive_email import receive_email
from backend.app.workflows.nodes.route_by_validation import route_by_validation
from backend.app.workflows.nodes.validate_fields import validate_fields
from backend.app.workflows.states import WorkflowState


def build_workflow_graph() -> StateGraph:
    graph = StateGraph(WorkflowState)

    graph.add_node("receive_email", receive_email)
    graph.add_node("extract_task", extract_task)
    graph.add_node("validate_fields", validate_fields)
    graph.add_node("draft_missing_info_email", draft_missing_info_email)
    graph.add_node("plan_schedule", plan_schedule)
    graph.add_node("create_calendar_event", create_calendar_event)
    graph.add_node("dispatch_task", dispatch_task)

    graph.set_entry_point("receive_email")
    graph.add_edge("receive_email", "extract_task")
    graph.add_edge("extract_task", "validate_fields")
    graph.add_conditional_edges(
        "validate_fields",
        route_by_validation,
        {
            "draft_missing_info_email": "draft_missing_info_email",
            "plan_schedule": "plan_schedule",
        },
    )
    graph.add_edge("draft_missing_info_email", END)
    graph.add_edge("plan_schedule", "create_calendar_event")
    graph.add_edge("create_calendar_event", "dispatch_task")
    graph.add_edge("dispatch_task", END)

    return graph


def compile_workflow() -> Any:
    graph = build_workflow_graph()
    return graph.compile()
