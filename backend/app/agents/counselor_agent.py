"""FR-8 Supervisor — the unified career counselor that remembers everything.

Each turn is grounded in a freshly-assembled context snapshot of the whole
journey, so the counselor answers "what should I do next?" with full memory.
"""
from __future__ import annotations

from collections.abc import AsyncIterator

from agents import Agent, Runner
from openai.types.responses import ResponseTextDeltaEvent

from ..models_config import MODEL_SMART
from .discovery_agent import session_for
from .runtime import groq_model


def _instructions(context: str) -> str:
    return f"""You are this candidate's dedicated AI career counselor — an experienced Engineering \
Manager who has read their entire history and never makes them repeat themselves.

Style: warm, specific, and actionable. Ground every piece of advice in their ACTUAL profile, assessment \
gaps, roadmap progress, and interview practice — reference specifics (the 40% latency win, the Cloud/DevOps \
gap, a roadmap milestone). When they ask what to do, give a concrete next step and explain why. Keep replies \
focused (3-6 sentences) unless they ask for depth. Be honest and encouraging; never guarantee outcomes; \
remind them gently that this is self-prep guidance when giving big decisions.

WHAT YOU KNOW ABOUT THEM (their journey so far):
{context}"""


def build_counselor(context: str) -> Agent:
    return Agent(
        name="Career Counselor",
        instructions=_instructions(context),
        model=groq_model(MODEL_SMART),
    )


async def generate_opener(context: str) -> str:
    agent = build_counselor(context)
    result = await Runner.run(
        agent,
        "Greet me by name if you know it, then in 2-3 sentences tell me the single most useful "
        "next step right now based on everything you know about my journey.",
    )
    return str(result.final_output)


async def stream_counselor(
    session_id: str, context: str, message: str
) -> AsyncIterator[str]:
    agent = build_counselor(context)
    result = Runner.run_streamed(agent, message, session=session_for(session_id))
    async for event in result.stream_events():
        if event.type == "raw_response_event" and isinstance(event.data, ResponseTextDeltaEvent):
            if event.data.delta:
                yield event.data.delta
