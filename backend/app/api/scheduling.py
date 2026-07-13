from __future__ import annotations

from datetime import datetime
from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.app.agents.calendar_planning_agent import ScheduleBlock, ScheduleSuggestion
from backend.app.services.cache import query_cache
from backend.app.services.queues.scheduling_queue import get_scheduling_queue

router = APIRouter(prefix="/api/scheduling", tags=["scheduling"])


class ScheduleBlockRequest(BaseModel):
    start_time: str
    end_time: str
    hours: float
    description: str = ""


class ScheduleBlockResponse(BaseModel):
    start_time: str
    end_time: str
    hours: float
    description: str


class ScheduleSuggestionResponse(BaseModel):
    blocks: list[ScheduleBlockResponse]
    total_hours: float
    fits_deadline: bool
    confidence: float


class SchedulingQueueItemResponse(BaseModel):
    ticket_id: str
    suggestion: ScheduleSuggestionResponse
    status: str
    created_at: str
    confidence: float
    confidence_indicator: dict[str, str]


class ApproveScheduleRequest(BaseModel):
    selected_blocks: list[ScheduleBlockRequest] | None = None


class DeclineScheduleRequest(BaseModel):
    reason: str | None = None


class ModifyScheduleRequest(BaseModel):
    blocks: list[ScheduleBlockRequest]


def _block_to_response(block: ScheduleBlock) -> ScheduleBlockResponse:
    return ScheduleBlockResponse(
        start_time=block.start_time.isoformat(),
        end_time=block.end_time.isoformat(),
        hours=block.hours,
        description=block.description,
    )


def _suggestion_to_response(
    suggestion: ScheduleSuggestion,
) -> ScheduleSuggestionResponse:
    return ScheduleSuggestionResponse(
        blocks=[_block_to_response(b) for b in suggestion.blocks],
        total_hours=suggestion.total_hours,
        fits_deadline=suggestion.fits_deadline,
        confidence=suggestion.confidence,
    )


def _item_to_response(item: Any) -> SchedulingQueueItemResponse:
    return SchedulingQueueItemResponse(
        ticket_id=str(item.ticket_id),
        suggestion=_suggestion_to_response(item.suggestion),
        status=item.status,
        created_at=item.created_at.isoformat(),
        confidence=item.confidence,
        confidence_indicator=item.confidence_indicator,
    )


@router.get("/queue", response_model=list[SchedulingQueueItemResponse])
async def get_scheduling_queue_endpoint() -> list[SchedulingQueueItemResponse]:
    queue = get_scheduling_queue()
    items = await queue.get_queue()
    return [_item_to_response(item) for item in items]


@router.get("/queue/{ticket_id}", response_model=SchedulingQueueItemResponse)
async def get_scheduling_item(ticket_id: str) -> SchedulingQueueItemResponse:
    queue = get_scheduling_queue()
    item = await queue.get_item(ticket_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Scheduling item not found")
    return _item_to_response(item)


@router.post("/queue/{ticket_id}/approve", response_model=SchedulingQueueItemResponse)
async def approve_schedule(
    ticket_id: str,
    request: ApproveScheduleRequest | None = None,
) -> SchedulingQueueItemResponse:
    queue = get_scheduling_queue()
    selected_blocks = None
    if request and request.selected_blocks:
        selected_blocks = [
            ScheduleBlock(
                start_time=datetime.fromisoformat(b.start_time),
                end_time=datetime.fromisoformat(b.end_time),
                hours=b.hours,
                description=b.description,
            )
            for b in request.selected_blocks
        ]

    item = await queue.approve_schedule(ticket_id, selected_blocks=selected_blocks)
    if item is None:
        raise HTTPException(status_code=404, detail="Scheduling item not found")
    if item.status != "APPROVED":
        raise HTTPException(status_code=409, detail="Item already processed")

    query_cache.clear()
    return _item_to_response(item)


@router.post("/queue/{ticket_id}/decline", response_model=SchedulingQueueItemResponse)
async def decline_schedule(
    ticket_id: str,
    request: DeclineScheduleRequest | None = None,
) -> SchedulingQueueItemResponse:
    queue = get_scheduling_queue()
    reason = request.reason if request else None
    item = await queue.decline_schedule(ticket_id, reason=reason)
    if item is None:
        raise HTTPException(status_code=404, detail="Scheduling item not found")
    if item.status != "DECLINED":
        raise HTTPException(status_code=409, detail="Item already processed")

    query_cache.clear()
    return _item_to_response(item)


@router.post("/queue/{ticket_id}/modify", response_model=SchedulingQueueItemResponse)
async def modify_schedule(
    ticket_id: str,
    request: ModifyScheduleRequest,
) -> SchedulingQueueItemResponse:
    queue = get_scheduling_queue()
    blocks = [
        ScheduleBlock(
            start_time=datetime.fromisoformat(b.start_time),
            end_time=datetime.fromisoformat(b.end_time),
            hours=b.hours,
            description=b.description,
        )
        for b in request.blocks
    ]
    item = await queue.modify_schedule(ticket_id, blocks)
    if item is None:
        raise HTTPException(status_code=404, detail="Scheduling item not found")

    query_cache.clear()
    return _item_to_response(item)
