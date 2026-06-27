"""Shared agent helpers."""
from __future__ import annotations

try:  # exported at top-level in recent SDK versions
    from agents import AgentOutputSchema
except ImportError:  # pragma: no cover - fallback for older layouts
    from agents.agent_output import AgentOutputSchema


def structured_output(model_type: type):
    """Wrap a Pydantic type as a NON-strict output schema.

    Groq's chat-completions endpoint does not fully support OpenAI strict
    json_schema, so we disable strict mode; the SDK still validates/parses the
    model's JSON into the Pydantic type.
    """
    return AgentOutputSchema(model_type, strict_json_schema=False)
