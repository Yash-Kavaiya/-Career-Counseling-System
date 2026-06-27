from __future__ import annotations

import json
from collections.abc import AsyncIterator

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from ..agents.discovery_agent import (
    DISCOVERY_TOPICS,
    generate_opener,
    session_for,
    stream_reply,
    update_coverage,
)
from ..agents.guardrails import REFUSAL, looks_like_injection
from ..database import SessionLocal
from ..deps import get_current_user, get_db
from ..models.session import CounselingSession
from ..models.user import User
from ..schemas.discovery import ChatMessage, DiscoveryMessageIn, DiscoveryState
from ..services import profile_service, session_service

router = APIRouter(prefix="/api/discovery", tags=["discovery"])


def _state(row: CounselingSession, messages: list[ChatMessage]) -> DiscoveryState:
    return DiscoveryState(
        session_id=row.id,
        stage=row.stage,
        all_topics=DISCOVERY_TOPICS,
        covered_topics=list(row.covered_topics or []),
        key_insights=list(row.key_insights or []),
        pending_questions=list(row.pending_questions or []),
        turns=row.turns or 0,
        messages=messages,
    )


async def _history(session_id: str) -> list[ChatMessage]:
    items = await session_for(session_id).get_items()
    out: list[ChatMessage] = []
    for it in items:
        role = it.get("role") if isinstance(it, dict) else None
        if role not in ("user", "assistant"):
            continue
        content = it.get("content")
        if isinstance(content, str):
            text = content
        elif isinstance(content, list):
            text = "".join(
                part.get("text", "")
                for part in content
                if isinstance(part, dict) and "text" in part
            )
        else:
            text = ""
        if text:
            out.append(ChatMessage(role=role, content=text))
    return out


@router.post("/start", response_model=DiscoveryState)
async def start(
    user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> DiscoveryState:
    profile = profile_service.get_profile(db, user.id)
    if not profile:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Add and save your resume first")
    row = session_service.new_session(db, user.id, "discovery")
    opener = await generate_opener(profile)
    await session_for(row.id).add_items([{"role": "assistant", "content": opener}])
    return _state(row, [ChatMessage(role="assistant", content=opener)])


@router.get("/latest", response_model=DiscoveryState)
async def latest(
    user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> DiscoveryState:
    row = session_service.latest_session(db, user.id, "discovery")
    if not row:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "No discovery session yet")
    return _state(row, await _history(row.id))


@router.get("/state/{session_id}", response_model=DiscoveryState)
async def state(
    session_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> DiscoveryState:
    row = session_service.get_session(db, user.id, session_id)
    if not row:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Session not found")
    return _state(row, await _history(session_id))


@router.post("/message")
async def message(
    body: DiscoveryMessageIn,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> StreamingResponse:
    row = session_service.get_session(db, user.id, body.session_id)
    if not row:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Session not found")
    profile = profile_service.get_profile(db, user.id)
    if not profile:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Profile missing")
    covered = list(row.covered_topics or [])
    pending = list(row.pending_questions or [])

    async def gen() -> AsyncIterator[str]:
        if looks_like_injection(body.message):
            yield f"data: {json.dumps({'delta': REFUSAL})}\n\n"
            yield 'data: {"done": true}\n\n'
            yield "data: [DONE]\n\n"
            return
        full = ""
        try:
            async for delta in stream_reply(
                body.session_id, profile, covered, pending, body.message
            ):
                full += delta
                yield f"data: {json.dumps({'delta': delta})}\n\n"
        except Exception as exc:  # noqa: BLE001
            yield f"data: {json.dumps({'error': str(exc)})}\n\n"
            return

        # Post-stream: update coverage state in a fresh DB session.
        try:
            exchange = f"COUNSELOR ASKED: {full}\n\nCANDIDATE REPLIED: {body.message}"
            upd = await update_coverage(profile, exchange, covered)
            valid_keys = {t.key for t in DISCOVERY_TOPICS}
            newly = [k for k in upd.newly_covered if k in valid_keys]
            with SessionLocal() as wdb:
                fresh = wdb.get(CounselingSession, body.session_id)
                if fresh:
                    fresh = session_service.apply_coverage(
                        wdb, fresh, newly_covered=newly, insights=upd.key_insights, pending=upd.pending_questions
                    )
                    payload = {
                        "done": True,
                        "covered_topics": list(fresh.covered_topics or []),
                        "key_insights": list(fresh.key_insights or []),
                        "pending_questions": list(fresh.pending_questions or []),
                        "turns": fresh.turns or 0,
                    }
                    yield f"data: {json.dumps(payload)}\n\n"
                else:
                    yield f"data: {json.dumps({'done': True})}\n\n"
        except Exception:  # noqa: BLE001 - coverage is best-effort
            yield f"data: {json.dumps({'done': True})}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(gen(), media_type="text/event-stream")
