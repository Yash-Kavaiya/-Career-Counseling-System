from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field

from .discovery import ChatMessage


class CounselorMessageIn(BaseModel):
    session_id: str
    message: str


class CounselorState(BaseModel):
    session_id: str
    messages: list[ChatMessage] = Field(default_factory=list)


class Overview(BaseModel):
    has_profile: bool
    profile_name: Optional[str] = None
    has_assessment: bool
    readiness: Optional[int] = None
    target_role: Optional[str] = None
    has_roadmap: bool
    roadmap_done: int = 0
    roadmap_total: int = 0
    discovery_turns: int = 0
    discovery_covered: int = 0
    discovery_total: int = 0
    latest_insight: Optional[str] = None
    interview_turns: int = 0
