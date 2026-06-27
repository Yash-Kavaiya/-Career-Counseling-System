"""Bind the OpenAI Agents SDK to Groq's OpenAI-compatible endpoint.

We build explicit `OpenAIChatCompletionsModel` instances (rather than passing
model-name strings) so the SDK's MultiProvider does not reinterpret provider
prefixes like ``openai/`` — Groq needs the literal model id (e.g.
``openai/gpt-oss-120b``). Groq serves chat-completions only and has no OpenAI
tracing backend, so tracing is disabled.
"""
from __future__ import annotations

import logging

from agents import OpenAIChatCompletionsModel, set_tracing_disabled
from openai import AsyncOpenAI

from ..config import settings

logger = logging.getLogger(__name__)

_client: AsyncOpenAI | None = None


def configure_groq() -> bool:
    """Initialise the shared Groq client. Returns True if a key was present."""
    global _client
    if _client is not None:
        return True
    if not settings.groq_api_key:
        logger.warning("GROQ_API_KEY not set — agent calls will fail until configured.")
        return False
    _client = AsyncOpenAI(base_url=settings.groq_base_url, api_key=settings.groq_api_key)
    set_tracing_disabled(True)
    logger.info("Agents SDK bound to Groq at %s", settings.groq_base_url)
    return True


def groq_model(name: str) -> OpenAIChatCompletionsModel:
    """Return a Model that calls `name` on Groq via chat-completions."""
    if _client is None and not configure_groq():
        raise RuntimeError("GROQ_API_KEY not configured")
    assert _client is not None
    return OpenAIChatCompletionsModel(model=name, openai_client=_client)
