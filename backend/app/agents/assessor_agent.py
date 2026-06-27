"""FR-3 Assessor — evidence-based strengths, gaps, and a skill radar."""
from __future__ import annotations

from agents import Agent, Runner

from ..models_config import MODEL_STRUCT
from ..schemas.assessment import Assessment
from ..schemas.profile import CandidateProfile
from ..services.profile_text import profile_summary
from .common import structured_output
from .runtime import groq_model

ASSESSOR_INSTRUCTIONS = """You are a senior Engineering Manager assessing a candidate's readiness for \
their target role, the way you would before forwarding a profile to a hiring panel.

Be honest but encouraging, and ALWAYS ground claims in concrete evidence from the resume or the \
discovery conversation. Avoid generic filler.

Produce:
- target_role and level: infer from the candidate's stated target roles/preferences; if unstated, infer \
  the most likely next step (e.g. service-company SDE with 3-4y → product SDE-2).
- summary: 2-3 honest sentences on overall fit.
- readiness_score (0-100): holistic readiness for that specific role and level.
- radar: 5-7 dimensions that actually matter for the target role (e.g. System Design, Backend, \
  Frontend, Cloud/DevOps, Data, Leadership, Communication). For each, score the candidate (0-10) and the \
  target level (0-10) for the role. Be calibrated to the real market bar — do not inflate.
- strengths: each with concrete evidence.
- gaps: each with a severity (low/medium/high/critical), the business impact for the target role, and a \
  concrete first step to close it. Order by importance.

Use the discovery insights as first-class evidence alongside the resume."""


def _assessor() -> Agent:
    return Agent(
        name="Assessor",
        instructions=ASSESSOR_INSTRUCTIONS,
        model=groq_model(MODEL_STRUCT),
        output_type=structured_output(Assessment),
    )


async def run_assessment(
    profile: CandidateProfile, discovery_insights: list[str]
) -> Assessment:
    insights = "\n".join(f"- {i}" for i in discovery_insights) or "(none yet)"
    prompt = (
        f"CANDIDATE PROFILE:\n{profile_summary(profile)}\n\n"
        f"DISCOVERY INSIGHTS:\n{insights}\n\n"
        "Assess this candidate for their target role."
    )
    result = await Runner.run(_assessor(), prompt)
    return result.final_output
