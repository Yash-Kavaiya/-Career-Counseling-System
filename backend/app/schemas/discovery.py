from __future__ import annotations

from pydantic import BaseModel, Field


class Topic(BaseModel):
    key: str
    label: str


class ChatMessage(BaseModel):
    role: str  # "user" | "assistant"
    content: str


class DiscoveryMessageIn(BaseModel):
    session_id: str
    message: str


class CoverageUpdate(BaseModel):
    """Structured update produced after each discovery exchange."""

    newly_covered: list[str] = Field(
        default_factory=list, description="Topic keys now substantively covered"
    )
    key_insights: list[str] = Field(
        default_factory=list, description="Concise new facts learned this turn"
    )
    pending_questions: list[str] = Field(
        default_factory=list, description="Useful follow-ups still open"
    )


class DiscoveryState(BaseModel):
    session_id: str
    stage: str
    all_topics: list[Topic]
    covered_topics: list[str]
    key_insights: list[str]
    pending_questions: list[str]
    turns: int
    messages: list[ChatMessage] = Field(default_factory=list)
