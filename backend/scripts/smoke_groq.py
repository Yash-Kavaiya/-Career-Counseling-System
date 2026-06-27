"""Smoke test: verify the OpenAI Agents SDK can talk to Groq.

Run from backend/:  uv run python -m scripts.smoke_groq
"""
from __future__ import annotations

import asyncio

from agents import Agent, Runner

from app.agents.runtime import configure_groq, groq_model
from app.models_config import MODEL_FAST


async def main() -> None:
    if not configure_groq():
        raise SystemExit("GROQ_API_KEY not set in backend/.env")

    agent = Agent(
        name="Smoke",
        instructions="You are a career counselor. Reply in one short sentence.",
        model=groq_model(MODEL_FAST),
    )
    result = await Runner.run(agent, "Say hello and name one job-search tip.")
    print("MODEL:", MODEL_FAST)
    print("OUTPUT:", result.final_output)


if __name__ == "__main__":
    asyncio.run(main())
