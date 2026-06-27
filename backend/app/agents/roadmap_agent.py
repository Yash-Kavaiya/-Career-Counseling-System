"""FR-7 Roadmap — prioritized, time-boxed plan to close the top gaps."""
from __future__ import annotations

from agents import Agent, Runner

from ..models_config import MODEL_STRUCT
from ..schemas.assessment import Assessment
from ..schemas.profile import CandidateProfile
from ..schemas.roadmap import Roadmap
from ..services.profile_text import profile_summary
from .common import structured_output
from .runtime import groq_model

ROADMAP_INSTRUCTIONS = """You are a pragmatic engineering mentor building a focused, time-boxed learning \
roadmap to close a candidate's most important gaps for their target role.

Rules:
- Address the TOP 3-5 gaps only — do not overwhelm. Order items by priority (1 = highest impact).
- For each item: a concrete action, why it matters for the target role, an HONEST estimated_weeks (assume \
they have a full-time job), 2-4 real, well-known resources (mix free and paid; include India-relevant ones \
like NPTEL where apt, plus widely-known ones such as ByteByteGo / "Grokking the System Design Interview", \
official docs, Kubernetes "Kubernetes the Hard Way", etc.), and 2-4 checkable milestones.
- Prefer quick wins early. Only include a resource url if you are confident it is correct; otherwise leave it null.
- Ground the plan in the candidate's actual gaps and current level."""


def _roadmap_agent() -> Agent:
    return Agent(
        name="Roadmap Builder",
        instructions=ROADMAP_INSTRUCTIONS,
        model=groq_model(MODEL_STRUCT),
        output_type=structured_output(Roadmap),
    )


async def generate_roadmap(profile: CandidateProfile, assessment: Assessment) -> Roadmap:
    gaps = "\n".join(
        f"- [{g.severity}] {g.title}: {g.business_impact}" for g in assessment.gaps
    )
    prompt = (
        f"CANDIDATE:\n{profile_summary(profile)}\n\n"
        f"TARGET: {assessment.target_role} ({assessment.level}), "
        f"readiness {assessment.readiness_score}/100\n\n"
        f"GAPS TO CLOSE:\n{gaps}\n\nBuild the learning roadmap."
    )
    result = await Runner.run(_roadmap_agent(), prompt)
    return result.final_output
