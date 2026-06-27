"""Central model routing for the Groq-hosted models used across agents.

All names are swappable here so cost/latency can be tuned in one place.
Verified available on the provided Groq key (GET /openai/v1/models).

IMPORTANT — Groq structured outputs: only some models support
`response_format=json_schema` (the gpt-oss-* and llama-4-* families). The
llama-3.x models are great for *free-form* chat but reject json_schema, so any
agent that uses `output_type=` MUST use a MODEL_STRUCT* / MODEL_VISION model.
See https://console.groq.com/docs/structured-outputs#supported-models
"""

# Free-form conversation (no structured output)
MODEL_FAST = "llama-3.1-8b-instant"          # cheap/simple turns, coverage updates
MODEL_SMART = "llama-3.3-70b-versatile"      # discovery & interview chat, supervisor

# Structured output (json_schema-capable, non-reasoning → reliable constrained decode)
MODEL_STRUCT = "meta-llama/llama-4-scout-17b-16e-instruct"  # parser, assessor, job-match, roadmap
MODEL_STRUCT_FAST = "openai/gpt-oss-20b"     # lighter structured tasks
MODEL_REASON = "openai/gpt-oss-120b"         # deep reasoning: answer evaluation

# Multimodal (image / scanned resumes) — also json_schema-capable
MODEL_VISION = "meta-llama/llama-4-scout-17b-16e-instruct"

# Prompt-injection input guard
MODEL_GUARD = "meta-llama/llama-prompt-guard-2-86m"
