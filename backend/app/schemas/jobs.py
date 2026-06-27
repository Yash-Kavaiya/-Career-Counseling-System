from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class JobOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    company: str
    location: str
    remote: str
    salary_band: str
    tech: list[str]
    source: str


class JDPasteIn(BaseModel):
    title: str
    company: str = ""
    location: str = ""
    remote: str = ""
    jd_text: str


class JobMatch(BaseModel):
    job_id: int
    fit_score: int = Field(ge=0, le=100)
    reasons: list[str] = Field(description="Why this role fits, with evidence")
    missing_pieces: list[str] = Field(description="What's lacking vs the JD")
    talking_points: list[str] = Field(description="How to position in the application")


class JobMatchResult(BaseModel):
    matches: list[JobMatch]


class MatchView(BaseModel):
    """A match joined with the job details, for the frontend."""

    job: JobOut
    fit_score: int
    reasons: list[str]
    missing_pieces: list[str]
    talking_points: list[str]
