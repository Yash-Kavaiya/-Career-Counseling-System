from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


class Resource(BaseModel):
    name: str
    url: Optional[str] = Field(default=None, description="Only if confidently correct")
    type: str = Field(description="course | book | practice | project | video | doc")
    is_free: bool = True


class Milestone(BaseModel):
    title: str
    done: bool = False


class RoadmapItem(BaseModel):
    priority: int = Field(ge=1, description="1 = highest impact")
    title: str
    gap: str = Field(description="The gap this item closes")
    action: str
    why_it_matters: str
    estimated_weeks: int = Field(ge=1)
    resources: list[Resource]
    milestones: list[Milestone]


class Roadmap(BaseModel):
    target_role: str
    summary: str
    items: list[RoadmapItem]


class RoadmapEnvelope(BaseModel):
    roadmap: Roadmap
    saved: bool = False


class MilestoneToggle(BaseModel):
    item_index: int
    milestone_index: int
    done: bool
