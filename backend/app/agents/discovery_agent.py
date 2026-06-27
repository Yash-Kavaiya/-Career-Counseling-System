"""FR-2 Discovery — adaptive, memory-backed counseling conversation.

The conversational agent (free-form, llama-3.3-70b) asks one targeted question
per turn, grounded by the profile and the live coverage state injected into its
instructions. A separate structured "coverage tracker" updates which topics are
now covered so the counselor never repeats itself.
"""
from __future__ import annotations

from collections.abc import AsyncIterator

from agents import Agent, Runner, SQLiteSession
from openai.types.responses import ResponseTextDeltaEvent

from ..config import settings
from ..models_config import MODEL_SMART, MODEL_STRUCT
from ..schemas.discovery import CoverageUpdate, Topic
from ..schemas.profile import CandidateProfile
from ..services.profile_text import profile_summary
from .common import structured_output
from .runtime import groq_model

DISCOVERY_TOPICS: list[Topic] = [
    Topic(key="achievements", label="Achievement depth — the how & measured impact"),
    Topic(key="system_design", label="System design / scale experience"),
    Topic(key="leadership", label="Leadership & collaboration (STAR stories)"),
    Topic(key="compensation", label="Current CTC & expectations"),
    Topic(key="targets", label="Target companies & role level"),
    Topic(key="gap", label="Career-gap context & activities"),
    Topic(key="tech_depth", label="Depth on key technologies"),
    Topic(key="motivation", label="Motivation & what matters (WLB, growth)"),
    Topic(key="constraints", label="Constraints — notice, location, remote"),
]


def _instructions(profile: CandidateProfile, covered: list[str], pending: list[str]) -> str:
    covered_labels = [t.label for t in DISCOVERY_TOPICS if t.key in covered]
    remaining = [t.label for t in DISCOVERY_TOPICS if t.key not in covered]
    flags = "; ".join(f"{f.field}: {f.reason}" for f in profile.uncertainty_flags) or "none"
    return f"""You are an experienced Engineering Manager acting as a warm, sharp career counselor. \
You have carefully read this candidate's resume and are now having a discovery conversation to fill \
gaps and surface their real goals and constraints.

RULES:
- Ask EXACTLY ONE focused question per turn — specific and evidence-based, referencing their actual \
resume (e.g. the 40% latency win, the mentoring, the gap). No generic questions.
- NEVER revisit a topic already covered. Build on what they just said.
- Briefly acknowledge their previous answer (one clause), then ask the next best question.
- Prioritize the uncertainty flags and the still-to-explore topics, most important first.
- Warm, concise, conversational — 2 to 4 sentences, no bullet lists, no preamble.
- When everything important is covered, say so and summarize what you learned instead of asking more.

CANDIDATE PROFILE:
{profile_summary(profile)}

UNCERTAINTY FLAGS TO RESOLVE: {flags}
ALREADY COVERED (do NOT revisit): {', '.join(covered_labels) or 'nothing yet'}
STILL TO EXPLORE (prioritize): {', '.join(remaining) or 'all covered — synthesize & confirm goals'}
OPEN FOLLOW-UPS: {'; '.join(pending) or 'none'}"""


def build_discovery_agent(
    profile: CandidateProfile, covered: list[str], pending: list[str]
) -> Agent:
    return Agent(
        name="Discovery Counselor",
        instructions=_instructions(profile, covered, pending),
        model=groq_model(MODEL_SMART),
    )


def session_for(session_id: str) -> SQLiteSession:
    return SQLiteSession(session_id, settings.agent_sessions_db)


async def generate_opener(profile: CandidateProfile) -> str:
    agent = build_discovery_agent(profile, [], [])
    result = await Runner.run(
        agent,
        "Begin the discovery session. Greet me in one friendly sentence, then ask your single most "
        "important first question based on my resume.",
    )
    return str(result.final_output)


async def stream_reply(
    session_id: str,
    profile: CandidateProfile,
    covered: list[str],
    pending: list[str],
    user_message: str,
) -> AsyncIterator[str]:
    agent = build_discovery_agent(profile, covered, pending)
    result = Runner.run_streamed(agent, user_message, session=session_for(session_id))
    async for event in result.stream_events():
        if event.type == "raw_response_event" and isinstance(event.data, ResponseTextDeltaEvent):
            if event.data.delta:
                yield event.data.delta


async def update_coverage(
    profile: CandidateProfile, exchange: str, covered: list[str]
) -> CoverageUpdate:
    topics_txt = "\n".join(f"- {t.key}: {t.label}" for t in DISCOVERY_TOPICS)
    agent = Agent(
        name="Coverage Tracker",
        instructions=f"""You track which discovery topics are now substantively covered in a career \
counseling conversation.

TOPICS (use these exact keys):
{topics_txt}

Already covered: {', '.join(covered) or 'none'}.

Given the latest exchange, return:
- newly_covered: topic KEYS that just received a substantive answer (omit if the answer was vague/skipped)
- key_insights: 1-3 short concrete facts learned
- pending_questions: useful follow-ups still open
Only use keys from the list above.""",
        model=groq_model(MODEL_STRUCT),
        output_type=structured_output(CoverageUpdate),
    )
    result = await Runner.run(agent, exchange)
    return result.final_output
