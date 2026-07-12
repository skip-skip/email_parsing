from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.calendar_event import CalendarEvent
from backend.app.models.ticket import Ticket
from backend.app.services.database import get_db

router = APIRouter(prefix="/api/tickets", tags=["tickets"])

ACTIVE_STATUSES = ("ACCEPTED", "CALENDAR_CREATED", "IN_PROGRESS")


class CalendarEventResponse(BaseModel):
    calendar_event_id: str
    outlook_event_id: str | None
    start_time: str
    end_time: str
    duration: float
    status: str


class TicketResponse(BaseModel):
    ticket_id: str
    status: str
    client: str | None
    contact: str | None
    project_number: str | None
    task_description: str | None
    deadline: str | None
    budget_hours: float | None
    estimated_hours: float | None
    priority: int
    calendar_event_id: str | None
    conversation_id: str | None
    created_at: str
    updated_at: str | None
    calendar_events: list[CalendarEventResponse]


def _calendar_event_to_response(event: CalendarEvent) -> CalendarEventResponse:
    return CalendarEventResponse(
        calendar_event_id=str(event.calendar_event_id),
        outlook_event_id=event.outlook_event_id,
        start_time=event.start_time.isoformat(),
        end_time=event.end_time.isoformat(),
        duration=event.duration,
        status=event.status,
    )


def _ticket_to_response(ticket: Ticket, events: list[CalendarEvent]) -> TicketResponse:
    return TicketResponse(
        ticket_id=str(ticket.ticket_id),
        status=ticket.status,
        client=ticket.client,
        contact=ticket.contact,
        project_number=ticket.project_number,
        task_description=ticket.task_description,
        deadline=ticket.deadline.isoformat() if ticket.deadline else None,
        budget_hours=ticket.budget_hours,
        estimated_hours=ticket.estimated_hours,
        priority=ticket.priority,
        calendar_event_id=ticket.calendar_event_id,
        conversation_id=ticket.conversation_id,
        created_at=ticket.created_at.isoformat(),
        updated_at=ticket.updated_at.isoformat() if ticket.updated_at else None,
        calendar_events=[_calendar_event_to_response(e) for e in events],
    )


@router.get("/active", response_model=list[TicketResponse])
async def list_active_tickets(
    status: str | None = Query(None, description="Filter by a single status"),
    client: str | None = Query(None, description="Filter by client name (case-insensitive partial match)"),
    sort_by: str = Query("deadline", description="Sort field: deadline, created_at, priority, client"),
    sort_dir: str = Query("asc", description="Sort direction: asc or desc"),
    db: AsyncSession = Depends(get_db),
) -> list[TicketResponse]:
    statuses = [status.upper()] if status else list(ACTIVE_STATUSES)
    query = select(Ticket).where(Ticket.status.in_(statuses))

    if client:
        query = query.where(Ticket.client.ilike(f"%{client}%"))

    sort_column_map = {
        "deadline": Ticket.deadline,
        "created_at": Ticket.created_at,
        "priority": Ticket.priority,
        "client": Ticket.client,
    }
    sort_col = sort_column_map.get(sort_by, Ticket.deadline)
    if sort_dir == "desc":
        query = query.order_by(sort_col.desc().nullslast())
    else:
        query = query.order_by(sort_col.asc().nullsfirst())

    result = await db.execute(query)
    tickets = list(result.scalars().all())

    ticket_ids = [t.ticket_id for t in tickets]
    events_query = select(CalendarEvent).where(CalendarEvent.ticket_id.in_(ticket_ids))
    events_result = await db.execute(events_query)
    all_events = list(events_result.scalars().all())
    events_by_ticket: dict[uuid.UUID, list[CalendarEvent]] = {}
    for event in all_events:
        events_by_ticket.setdefault(event.ticket_id, []).append(event)

    return [
        _ticket_to_response(t, events_by_ticket.get(t.ticket_id, []))
        for t in tickets
    ]


@router.get("/{ticket_id}", response_model=TicketResponse)
async def get_ticket(
    ticket_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> TicketResponse:
    result = await db.execute(select(Ticket).where(Ticket.ticket_id == ticket_id))
    ticket = result.scalar_one_or_none()
    if ticket is None:
        raise HTTPException(status_code=404, detail="Ticket not found")

    events_result = await db.execute(
        select(CalendarEvent).where(CalendarEvent.ticket_id == ticket_id)
    )
    events = list(events_result.scalars().all())

    return _ticket_to_response(ticket, events)
