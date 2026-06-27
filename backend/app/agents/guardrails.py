"""Input guardrails.

Output safety is handled by the always-on disclaimer (frontend) and the agents'
system prompts (never guarantee outcomes; flag uncertainty). For input, this
module offers a cheap prompt-injection heuristic used by the chat endpoints.
Groq also hosts ``meta-llama/llama-prompt-guard-2-86m`` (see
``models_config.MODEL_GUARD``) for a stronger model-based guard when needed.
"""
from __future__ import annotations

_INJECTION_MARKERS = (
    "ignore previous",
    "ignore all previous",
    "disregard your instructions",
    "disregard the above",
    "reveal your system prompt",
    "reveal your prompt",
    "you are now",
    "from now on you are",
    "print your instructions",
    "show your system prompt",
)


def looks_like_injection(text: str) -> bool:
    """Heuristic check for obvious prompt-injection attempts."""
    t = text.lower()
    return any(marker in t for marker in _INJECTION_MARKERS)


REFUSAL = (
    "I'm here to help with your career — let's keep our focus there. "
    "Could you rephrase that as a career question?"
)
