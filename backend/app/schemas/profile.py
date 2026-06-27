"""Canonical candidate profile — the structured output of the parser agent and
the shared state consumed by every downstream agent (assessment, jobs, etc.)."""
from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, Field, field_validator


class Achievement(BaseModel):
    description: str
    metric: Optional[str] = Field(
        default=None, description="Quantified impact, e.g. '40% latency reduction'"
    )


class Experience(BaseModel):
    company: str
    client: Optional[str] = Field(default=None, description="End client for service companies")
    role: str
    start: Optional[str] = Field(default=None, description="Free-form start date as written")
    end: Optional[str] = Field(default=None, description="End date or 'Present'")
    is_current: bool = False
    location: Optional[str] = None
    tech: list[str] = Field(default_factory=list)
    achievements: list[Achievement] = Field(default_factory=list)
    summary: Optional[str] = None


class Education(BaseModel):
    degree: str
    institution: str
    year: Optional[str] = None
    score: Optional[str] = Field(default=None, description="CGPA / percentage as written")


class Skill(BaseModel):
    name: str
    category: Optional[str] = Field(
        default=None, description="language | framework | cloud | database | tool | soft | other"
    )
    proficiency: Optional[Literal["beginner", "intermediate", "advanced", "expert"]] = None
    evidence: Optional[str] = Field(default=None, description="Where this skill is demonstrated")


class Project(BaseModel):
    name: str
    description: Optional[str] = None
    tech: list[str] = Field(default_factory=list)
    link: Optional[str] = None
    highlights: list[str] = Field(default_factory=list)


class Certification(BaseModel):
    name: str
    issuer: Optional[str] = None
    status: Optional[str] = Field(default=None, description="completed | in-progress")


class Preferences(BaseModel):
    current_ctc: Optional[str] = None
    expected_ctc: Optional[str] = None
    notice_period: Optional[str] = None
    locations: list[str] = Field(default_factory=list)
    remote_preference: Optional[str] = Field(
        default=None, description="remote | hybrid | onsite | flexible"
    )
    company_types: list[str] = Field(
        default_factory=list, description="product | service | startup | enterprise"
    )
    target_roles: list[str] = Field(
        default_factory=list, description="e.g. 'SDE-2 Backend', 'Engineering Manager'"
    )
    priorities: list[str] = Field(
        default_factory=list, description="e.g. 'work-life balance', 'growth', 'compensation'"
    )


class CareerGap(BaseModel):
    dates: Optional[str] = Field(default=None, description="e.g. 'Mar 2022 - Aug 2022'")
    reason: Optional[str] = Field(default=None, description="Stated reason if any")
    activities: Optional[str] = Field(
        default=None, description="Self-learning / side projects during the gap, if any"
    )


class UncertaintyFlag(BaseModel):
    field: str = Field(description="Profile field or area that is unclear/missing")
    reason: str = Field(description="Why it is uncertain — to drive a discovery question")
    confidence: float = Field(ge=0.0, le=1.0, description="0=guess, 1=certain")


class CandidateProfile(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    links: list[str] = Field(default_factory=list, description="LinkedIn, GitHub, portfolio")
    headline: Optional[str] = Field(default=None, description="e.g. 'SDE | 3.8y | Bangalore'")
    summary: Optional[str] = Field(default=None, description="2-3 line professional summary")
    total_experience_years: Optional[float] = None
    experiences: list[Experience] = Field(default_factory=list)
    education: list[Education] = Field(default_factory=list)
    skills: list[Skill] = Field(default_factory=list)
    projects: list[Project] = Field(default_factory=list)
    certifications: list[Certification] = Field(default_factory=list)
    preferences: Preferences = Field(default_factory=Preferences)
    career_gaps: list[CareerGap] = Field(default_factory=list)
    uncertainty_flags: list[UncertaintyFlag] = Field(default_factory=list)

    @field_validator("career_gaps", mode="before")
    @classmethod
    def _coerce_gaps(cls, v: object) -> object:
        # Accept either bare strings or structured objects from the model.
        if isinstance(v, list):
            return [{"reason": x} if isinstance(x, str) else x for x in v]
        return v


class ProfileEnvelope(BaseModel):
    """API response wrapping the profile plus persistence metadata."""

    profile: CandidateProfile
    version: int = 1
    saved: bool = False
