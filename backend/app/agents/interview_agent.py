"""FR-5/6 Mock interview — adaptive interviewer (streamed) + rubric evaluator."""
from __future__ import annotations

from collections.abc import AsyncIterator

from agents import Agent, Runner
from openai.types.responses import ResponseTextDeltaEvent

from ..models_config import MODEL_SMART, MODEL_STRUCT
from ..schemas.interview import AnswerFeedback
from ..schemas.profile import CandidateProfile
from ..services.profile_text import profile_summary
from .common import structured_output
from .discovery_agent import session_for  # shared SQLiteSession helper
from .runtime import groq_model


def _interviewer_instructions(profile: CandidateProfile, target_role: str, focus: str) -> str:
    return f"""You are a seasoned technical interviewer running a realistic mock interview for a \
{target_role} role. Make it feel like a real onsite.

RULES:
- Ask EXACTLY ONE question per turn. Mix technical (system design, deep-dives on their stack, problem \
solving) and behavioral (STAR) questions across the interview.
- Adapt to their answers: probe depth, follow up on vague/weak answers, move on when an answer is solid.
- Pay extra attention to these focus areas: {focus}.
- Reference their real background where natural. Briefly acknowledge their answer in one clause, then ask \
the next question.
- Keep questions crisp (1-3 sentences). After roughly 7 questions, conclude warmly and stop asking.

CANDIDATE:
{profile_summary(profile)}"""


def build_interviewer(profile: CandidateProfile, target_role: str, focus: str) -> Agent:
    return Agent(
        name="Interviewer",
        instructions=_interviewer_instructions(profile, target_role, focus),
        model=groq_model(MODEL_SMART),
    )


async def generate_first_question(
    profile: CandidateProfile, target_role: str, focus: str
) -> str:
    agent = build_interviewer(profile, target_role, focus)
    result = await Runner.run(
        agent,
        "Start the mock interview. Set the scene in one sentence, then ask your first question.",
    )
    return str(result.final_output)


async def stream_interviewer(
    session_id: str, profile: CandidateProfile, target_role: str, focus: str, answer: str
) -> AsyncIterator[str]:
    agent = build_interviewer(profile, target_role, focus)
    result = Runner.run_streamed(agent, answer, session=session_for(session_id))
    async for event in result.stream_events():
        if event.type == "raw_response_event" and isinstance(event.data, ResponseTextDeltaEvent):
            if event.data.delta:
                yield event.data.delta


EVALUATOR_INSTRUCTIONS = """You are a rigorous but fair interview evaluator. Given the QUESTION and the \
candidate's ANSWER, score each rubric dimension 0-10:
- correctness: technical accuracy / soundness
- clarity: how clearly it's communicated
- depth: insight, edge cases, tradeoffs considered
- structure: organization (STAR for behavioral; structured reasoning for technical)
- communication: conciseness and signal

Then give: overall (0-10), 1-3 concrete strengths, 1-3 concrete improvements, and a short better_answer \
outline showing what a strong answer covers. Be specific to THIS question and answer; do not be generous \
with scores for vague answers."""


def _evaluator() -> Agent:
    return Agent(
        name="Answer Evaluator",
        instructions=EVALUATOR_INSTRUCTIONS,
        model=groq_model(MODEL_STRUCT),
        output_type=structured_output(AnswerFeedback),
    )


async def evaluate_answer(question: str, answer: str) -> AnswerFeedback:
    result = await Runner.run(
        _evaluator(), f"QUESTION:\n{question}\n\nANSWER:\n{answer}"
    )
    return result.final_output
