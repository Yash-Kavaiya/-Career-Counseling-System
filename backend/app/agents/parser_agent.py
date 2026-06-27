"""FR-1 Parser agent — extracts a structured CandidateProfile from resume content."""
from __future__ import annotations

from agents import Agent, Runner

from ..models_config import MODEL_STRUCT, MODEL_VISION
from ..schemas.profile import CandidateProfile
from ..services.document import ResumeContent
from .common import structured_output
from .runtime import groq_model

PARSER_INSTRUCTIONS = """You are an experienced Engineering Manager who reads resumes the way a \
seasoned hiring manager does: you extract the real signal, infer sensibly, and notice what is \
missing or unclear.

Produce a clean, structured candidate profile. Rules:
- NEVER invent facts. Infer only what is strongly supported; otherwise leave fields empty and flag them.
- Handle messy Indian tech resumes well:
  * Service companies — capture the END CLIENT separately from the employer.
  * Notice period, current CTC and expected CTC are often buried in the objective/summary — extract them into preferences.
  * Career gaps — capture each with its dates and the stated reason if any (e.g. "family health").
  * Tier-2/3 colleges, CGPA vs percentage, and mixed responsibilities vs achievements.
- For each achievement, separate the ACTION from the quantified METRIC when one is present
  (e.g. action "optimized queries", metric "40% latency reduction").
- Infer skill proficiency from the DEPTH of evidence, not mere mentions ("(basic)", "some" → beginner).
- Populate preferences (notice period, CTC, locations, remote, company types like product/service,
  target roles, and priorities such as work-life balance) when stated or strongly implied.
- CRITICAL: for anything missing, ambiguous, contradictory, or low-confidence, add an uncertainty_flag
  with a concrete, actionable reason and a confidence score (0-1). These directly drive the discovery
  conversation. Good examples: "system design depth unknown — only CRUD microservices shown";
  "current CTC not stated"; "reason for 2022 gap given but learning during it unknown";
  "primary stack unclear — Java backend vs Node both present".

Return only the structured profile."""


def _parser_agent(model: str) -> Agent:
    return Agent(
        name="Resume Parser",
        instructions=PARSER_INSTRUCTIONS,
        model=groq_model(model),
        output_type=structured_output(CandidateProfile),
    )


async def parse_resume(content: ResumeContent) -> CandidateProfile:
    if content.images:
        parts: list[dict] = [
            {
                "type": "input_text",
                "text": "Parse this resume into the structured profile."
                + (f"\n\nExtracted text:\n{content.text}" if content.text else ""),
            }
        ]
        for url in content.image_data_urls():
            parts.append({"type": "input_image", "image_url": url})
        result = await Runner.run(
            _parser_agent(MODEL_VISION), [{"role": "user", "content": parts}]
        )
    else:
        prompt = f"Parse this resume into the structured profile.\n\nRESUME:\n{content.text}"
        result = await Runner.run(_parser_agent(MODEL_STRUCT), prompt)
    return result.final_output
