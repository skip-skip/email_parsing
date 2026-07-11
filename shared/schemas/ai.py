from typing import Any

from pydantic import BaseModel, Field


class ConfidenceScore(BaseModel):
    score: float = Field(ge=0.0, le=1.0)
    field: str
    reasoning: str | None = None


class AIDecision(BaseModel):
    model: str
    prompt_version: str
    prompt: str
    response: str
    parsed_json: dict[str, Any] = {}
    confidence: float = Field(ge=0.0, le=1.0)
    execution_time: float
