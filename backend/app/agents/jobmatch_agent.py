"""FR-4 Job Matcher — semantic pre-filter (embeddings) + LLM re-ranker with reasons."""
from __future__ import annotations

from agents import Agent, Runner

from ..models.job import Job
from ..models_config import MODEL_STRUCT
from ..schemas.assessment import Assessment
from ..schemas.jobs import JobMatchResult
from ..schemas.profile import CandidateProfile
from ..services.profile_text import profile_summary
from .common import structured_output
from .runtime import groq_model

MATCHER_INSTRUCTIONS = """You are a sharp technical recruiter and Engineering Manager matching a \
candidate to open roles. You explain WHY a role fits and how to position for it — something keyword \
search cannot do.

For each genuinely relevant role, return:
- job_id: exactly as given in [JOB n]
- fit_score (0-100): calibrated. Weigh tech overlap, seniority/level fit, location & remote compatibility, \
  salary vs the candidate's expectation, notice-period realism, and growth/company-type fit.
- reasons: 2-4 SPECIFIC reasons grounded in the candidate's actual evidence (e.g. the 40% latency win, \
  Spring Boot microservices, mentoring).
- missing_pieces: what the JD asks for that the candidate currently lacks.
- talking_points: concrete ways to position themselves for THIS role.

Only include roles genuinely worth applying to — skip poor fits entirely. Rank by fit_score descending. \
Be honest and calibrated, not generous."""


def _matcher() -> Agent:
    return Agent(
        name="Job Matcher",
        instructions=MATCHER_INSTRUCTIONS,
        model=groq_model(MODEL_STRUCT),
        output_type=structured_output(JobMatchResult),
    )


async def match_jobs(
    profile: CandidateProfile, assessment: Assessment | None, jobs: list[Job]
) -> JobMatchResult:
    a = ""
    if assessment:
        gaps = ", ".join(g.title for g in assessment.gaps)
        a = (
            f"\nASSESSMENT: target {assessment.target_role} ({assessment.level}), "
            f"readiness {assessment.readiness_score}/100. Key gaps: {gaps}.\n"
        )
    jobs_txt = "\n\n".join(
        f"[JOB {j.id}] {j.title} @ {j.company} — {j.location}, {j.remote}, {j.salary_band}\n"
        f"Tech: {', '.join(j.tech)}\n{j.jd_text}"
        for j in jobs
    )
    prompt = (
        f"CANDIDATE:\n{profile_summary(profile)}\n{a}\n"
        f"OPEN ROLES:\n{jobs_txt}\n\nReturn the best matches for this candidate."
    )
    result = await Runner.run(_matcher(), prompt)
    return result.final_output
