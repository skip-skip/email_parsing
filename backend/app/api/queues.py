from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.app.agents.email_draft_agent import DraftEmail
from backend.app.services.queues.missing_info_queue import MissingInfoQueue

router = APIRouter(prefix="/api/queues", tags=["queues"])

_queue = MissingInfoQueue()


class DraftEmailRequest(BaseModel):
    to: str
    subject: str
    body: str
    missing_fields: list[str]


class DraftEmailResponse(BaseModel):
    to: str
    subject: str
    body: str
    missing_fields: list[str]
    ticket_id: str


class QueueItemResponse(BaseModel):
    ticket_id: str
    draft_email: DraftEmailResponse
    missing_fields: list[str]
    created_at: str
    status: str


class ApproveRequest(BaseModel):
    edits: DraftEmailRequest | None = None


class RejectRequest(BaseModel):
    reason: str | None = None


def _queue_item_to_response(item: Any) -> QueueItemResponse:
    return QueueItemResponse(
        ticket_id=str(item.ticket_id),
        draft_email=DraftEmailResponse(
            to=item.draft_email.to,
            subject=item.draft_email.subject,
            body=item.draft_email.body,
            missing_fields=item.draft_email.missing_fields,
            ticket_id=str(item.draft_email.ticket_id),
        ),
        missing_fields=item.missing_fields,
        created_at=item.created_at.isoformat(),
        status=item.status,
    )


@router.get("/missing-info", response_model=list[QueueItemResponse])
async def get_missing_info_queue() -> list[QueueItemResponse]:
    items = await _queue.get_queue()
    return [_queue_item_to_response(item) for item in items]


@router.get("/missing-info/{ticket_id}", response_model=QueueItemResponse)
async def get_missing_info_item(ticket_id: str) -> QueueItemResponse:
    item = await _queue.get_item(ticket_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Queue item not found")
    return _queue_item_to_response(item)


@router.post("/missing-info/{ticket_id}/approve", response_model=QueueItemResponse)
async def approve_missing_info(
    ticket_id: str,
    request: ApproveRequest | None = None,
) -> QueueItemResponse:
    edits = None
    if request and request.edits:
        edits = DraftEmail(
            to=request.edits.to,
            subject=request.edits.subject,
            body=request.edits.body,
            missing_fields=request.edits.missing_fields,
            ticket_id=uuid.UUID(ticket_id),
        )

    item = await _queue.approve_item(ticket_id, edits=edits)
    if item is None:
        raise HTTPException(status_code=404, detail="Queue item not found")
    if item.status != "APPROVED":
        raise HTTPException(status_code=409, detail="Item already processed")

    return _queue_item_to_response(item)


@router.post("/missing-info/{ticket_id}/reject", response_model=QueueItemResponse)
async def reject_missing_info(
    ticket_id: str,
    request: RejectRequest | None = None,
) -> QueueItemResponse:
    reason = request.reason if request else None
    item = await _queue.reject_item(ticket_id, reason=reason)
    if item is None:
        raise HTTPException(status_code=404, detail="Queue item not found")
    if item.status != "REJECTED":
        raise HTTPException(status_code=409, detail="Item already processed")

    return _queue_item_to_response(item)


@router.put("/missing-info/{ticket_id}/draft", response_model=QueueItemResponse)
async def update_missing_info_draft(
    ticket_id: str,
    request: DraftEmailRequest,
) -> QueueItemResponse:
    new_draft = DraftEmail(
        to=request.to,
        subject=request.subject,
        body=request.body,
        missing_fields=request.missing_fields,
        ticket_id=uuid.UUID(ticket_id),
    )
    item = await _queue.update_draft(ticket_id, new_draft)
    if item is None:
        raise HTTPException(status_code=404, detail="Queue item not found")

    return _queue_item_to_response(item)
