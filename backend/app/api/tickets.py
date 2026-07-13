from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.calendar_event import CalendarEvent
from backend.app.models.ticket import Ticket
from backend.app.services.database import get_db
from backend.app.services.etag import compute_etag

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


class PaginatedTicketResponse(BaseModel):
    items: list[TicketResponse]
    total: int
    offset: int
    limit: int


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


@router.get("/active", response_model=PaginatedTicketResponse)
async def list_active_tickets(
    request: Request,
    status: str | None = Query(None, description="Filter by a single status"),
    client: str | None = Query(
        None, description="Filter by client name (case-insensitive partial match)"
    ),
    sort_by: str = Query(
        "deadline", description="Sort field: deadline, created_at, priority, client"
    ),
    sort_dir: str = Query("asc", description="Sort direction: asc or desc"),
    offset: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(50, ge=1, le=200, description="Maximum records to return"),
    db: AsyncSession = Depends(get_db),
) -> Response:
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

    # Count total matching records.
    count_query = select(func.count()).select_from(
        select(Ticket).where(Ticket.status.in_(statuses)).subquery()
    )
    if client:
        count_query = select(func.count()).select_from(
            select(Ticket)
            .where(Ticket.status.in_(statuses))
            .where(Ticket.client.ilike(f"%{client}%"))
            .subquery()
        )
    total_result = await db.execute(count_query)
    total = total_result.scalar_one()

    # Fetch paginated results.
    result = await db.execute(query.offset(offset).limit(limit))
    tickets = list(result.scalars().all())

    ticket_ids = [t.ticket_id for t in tickets]
    events_by_ticket: dict[uuid.UUID, list[CalendarEvent]] = {}
    if ticket_ids:
        events_query = select(CalendarEvent).where(
            CalendarEvent.ticket_id.in_(ticket_ids)
        )
        events_result = await db.execute(events_query)
        all_events = list(events_result.scalars().all())
        for event in all_events:
            events_by_ticket.setdefault(event.ticket_id, []).append(event)

    items = [
        _ticket_to_response(t, events_by_ticket.get(t.ticket_id, [])) for t in tickets
    ]
    body = PaginatedTicketResponse(items=items, total=total, offset=offset, limit=limit)
    etag = compute_etag(body.model_dump())

    if request.headers.get("if-none-match") == etag:
        return Response(status_code=304, headers={"ETag": etag})

    return Response(
        content=body.model_dump_json(),
        media_type="application/json",
        headers={"ETag": etag},
    )


@router.get("/{ticket_id}", response_model=TicketResponse)
async def get_ticket(
    ticket_id: uuid.UUID,
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> Response:
    result = await db.execute(select(Ticket).where(Ticket.ticket_id == ticket_id))
    ticket = result.scalar_one_or_none()
    if ticket is None:
        raise HTTPException(status_code=404, detail="Ticket not found")

    events_result = await db.execute(
        select(CalendarEvent).where(CalendarEvent.ticket_id == ticket_id)
    )
    events = list(events_result.scalars().all())

    body = _ticket_to_response(ticket, events)
    etag = compute_etag(body.model_dump())

    if request.headers.get("if-none-match") == etag:
        return Response(status_code=304, headers={"ETag": etag})

    return Response(
        content=body.model_dump_json(),
        media_type="application/json",
        headers={"ETag": etag},
    )
