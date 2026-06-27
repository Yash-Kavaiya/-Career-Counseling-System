from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class RadarAxis(BaseModel):
    axis: str = Field(description="Skill dimension, e.g. 'System Design'")
    score: float = Field(ge=0, le=10, description="Candidate's current level")
    target: float = Field(ge=0, le=10, description="Level expected for the target role")


class Strength(BaseModel):
    title: str
    evidence: str = Field(description="Concrete evidence from resume or discovery")


class Gap(BaseModel):
    title: str
    severity: Literal["low", "medium", "high", "critical"]
    business_impact: str = Field(description="Why this matters for the target role")
    how_to_close: str = Field(description="Concrete first step to close it")


class Assessment(BaseModel):
    target_role: str
    level: str = Field(description="e.g. 'SDE-2', 'Senior', 'EM'")
    summary: str = Field(description="2-3 sentence honest, encouraging read of fit")
    readiness_score: int = Field(ge=0, le=100, description="Overall readiness for the target role")
    radar: list[RadarAxis] = Field(description="5-7 dimensions relevant to the target role")
    strengths: list[Strength]
    gaps: list[Gap]


class AssessmentEnvelope(BaseModel):
    assessment: Assessment
    saved: bool = False
