# AI‑Native Career Counseling System

An AI career counselor that thinks like an experienced Engineering Manager: it parses a messy
resume, runs an adaptive discovery conversation, assesses strengths and gaps, matches jobs with
reasons, runs a rubric‑scored mock interview, builds a learning roadmap — and **remembers
everything across the whole journey**.

> ⚠️ **AI self‑prep assistant — suggestions only, not a substitute for professional career advice.**

**Stack:** Angular 20 (Globant “Green Book” design) · FastAPI · **OpenAI Agents SDK** running on
**Groq** · local embeddings (fastembed) · SQLite (zero‑infra).

---

## Why AI‑native

Traditional software is *Input → hard‑coded rules → Output* and collapses on the long tail of real
resumes. Here, specialist **agents** reason over **structured state + memory + tools**: they extract
signal, infer what’s missing, probe intelligently, explain their reasoning, and never repeat
themselves. The OpenAI Agents SDK provides the primitives — `Agent`, `Runner`, `SQLiteSession`
(memory), `@function_tool`, `output_type` (typed JSON), streaming — pointed at Groq’s
OpenAI‑compatible endpoint.

## Features (all implemented & verified)

| FR | Feature | What it does |
|----|---------|--------------|
| FR‑1 | **Resume parsing** | PDF/DOCX/TXT/image → canonical `CandidateProfile` with confidence/uncertainty flags. Editable review UI. Extracts notice period & CTC from objective lines, career gaps, service‑company clients. |
| FR‑2 | **Discovery chat** | Streaming, adaptive, **non‑repeating** questions grounded in the resume; live coverage tracking (9 topics) + insight extraction. |
| FR‑3 | **Assessment** | Evidence‑based strengths, severity‑ranked gaps with business impact, and a you‑vs‑target **skill radar**. |
| FR‑4 | **Job match** | Local‑embedding semantic pre‑filter + LLM re‑ranker → fit score, *why it fits*, *close before applying*, *how to position*. Paste your own JD. |
| FR‑5/6 | **Mock interview + evaluation** | Adaptive technical/behavioural interview (streamed) + rubric scoring (correctness, depth, structure, clarity, communication), better‑answer outline, readiness score. |
| FR‑7 | **Learning roadmap** | Prioritized, time‑boxed plan with resources (incl. India‑context like NPTEL) and checkable milestones with progress. |
| FR‑8 | **Memory & continuity** | Cross‑session memory feeds every step; a unified **Counselor chat** that answers “what next?” grounded in your whole journey; dashboard continuity (“last time we discussed…”, completion + progress). |

Plus: JWT auth + consent, prominent disclaimers, prompt‑injection input guard, and **data export +
delete** (DPDP/GDPR).

## Architecture

```
Angular 20 SPA  ──HTTPS / JWT──▶  FastAPI  ──▶  OpenAI Agents SDK ──▶ Groq
  (signals,                        (routers/         ├─ Parser · Discovery · Assessor
   standalone,                      services/        ├─ JobMatcher · Interviewer · Evaluator
   SSE streaming,                   agents)          ├─ Roadmap · Supervisor (counselor)
   Tailwind + Globant)                │              └─ tools / guardrails
                                      ▼
                       SQLite (SQLAlchemy ORM)  +  fastembed (local embeddings)
                       + SQLiteSession (agent conversation memory)
```

**Model routing** (`app/models_config.py`, all Groq, swappable):
- `llama-3.1-8b-instant` — fast/simple
- `llama-3.3-70b-versatile` — discovery & interview chat, supervisor (free‑form)
- `meta-llama/llama-4-scout-17b-16e-instruct` — **structured output** (parser, assessor, matcher, roadmap) and vision
- `openai/gpt-oss-120b` — deep reasoning (answer evaluation)
- `meta-llama/llama-prompt-guard-2-86m` — available for model‑based input guarding

> Note: Groq serves chat‑completions only and supports `json_schema` structured output on a subset
> of models (gpt‑oss‑*, llama‑4‑*) — hence the routing above. Embeddings run **locally** (Groq has no
> embeddings API).

## Prerequisites

- **Node 20+** and Angular CLI (`npm i -g @angular/cli`)
- **Python 3.11+** and [`uv`](https://docs.astral.sh/uv/)
- A **Groq API key** → https://console.groq.com

## Run it

### 1) Backend
```bash
cd backend
cp .env.example .env          # then set GROQ_API_KEY in .env
uv sync --python 3.11
uv run uvicorn app.main:app --reload --port 8000
# API docs at http://localhost:8000/docs
```

### 2) Frontend
```bash
cd frontend
npm install
ng serve                      # http://localhost:4200
```

Register an account, upload a resume (try the “Arjun” composite), and walk the journey:
**Resume → Discovery → Assessment → Jobs → Interview → Roadmap → Counselor**.

### Tests
```bash
cd backend && uv run pytest          # fast, no‑LLM unit tests
cd frontend && ng build              # type‑check / production build
```

## API overview

`/api/auth` register · login · me  ·  `/api/resume` parse · profile (GET/PUT)
`/api/discovery` start · message (SSE) · latest/state  ·  `/api/assessment` run · GET
`/api/jobs` match · paste · list  ·  `/api/interview` start · message (SSE) · latest
`/api/roadmap` generate · GET · milestone (PATCH)  ·  `/api/counselor` start · message (SSE) · latest
`/api/me` overview · export · DELETE

## Design system

The frontend follows Globant’s **“Green Book”**: white‑predominant canvas, bright‑green gradient
accents (`#00E676 → #00C853 → #64DD17`), near‑black `#111` text, **Space Grotesk** display + **Inter**
body, the forward‑arrow motif, and disciplined motion. Tokens live in
[`frontend/src/styles.css`](frontend/src/styles.css).

## Privacy & ethics

- Explicit **consent** at registration; PII processed to power counseling (sent to **Groq**).
- **Export** (full JSON) and **delete** (account + all data, clears conversation memory).
- Prominent disclaimers; agents never guarantee outcomes and flag low‑confidence inferences.
- Heuristic prompt‑injection input guard; `llama‑prompt‑guard‑2` available for stronger guarding.

## Project structure

```
backend/app/
  agents/      parser, discovery, assessor, jobmatch, interview, roadmap, counselor, runtime, guardrails
  models/      SQLAlchemy ORM (user, profile, session, assessment, job, interview, roadmap)
  schemas/     Pydantic (also used as agent output_type)
  routers/     auth, resume, discovery, assessment, jobs, interview, roadmap, counselor, overview
  services/    document, profile_text, embeddings, context, + per‑feature services
  seed/        curated_jobs.json
frontend/src/app/
  core/        services, models, auth interceptor/guard, SSE service
  features/    auth, dashboard, resume, discovery, assessment, jobs, interview, roadmap, counselor
  shared/      radar-chart, disclaimer-banner
```

## Notes / future work

Voice I/O (Groq Whisper is available), Hindi/Gujarati localization, profile‑update *proposals* after
sessions, Postgres + pgvector migration (the embeddings/ORM seams are ready), live job ingestion, and
a reflection/self‑improvement loop.

---

> **Security:** never commit `.env`. If a key was ever shared in plaintext, **rotate it**.
