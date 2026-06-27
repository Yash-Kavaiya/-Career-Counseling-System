from __future__ import annotations

import json
from collections.abc import AsyncIterator

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from ..agents.counselor_agent import generate_opener, stream_counselor
from ..agents.discovery_agent import session_for
from ..agents.guardrails import REFUSAL, looks_like_injection
from ..database import SessionLocal
from ..deps import get_current_user, get_db
from ..models.session import CounselingSession
from ..models.user import User
from ..schemas.counselor import CounselorMessageIn, CounselorState
from ..schemas.discovery import ChatMessage
from ..services import context_service, session_service
from .discovery import _history

router = APIRouter(prefix="/api/counselor", tags=["counselor"])


@router.post("/start", response_model=CounselorState)
async def start(
    user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> CounselorState:
    if not context_service.has_any(db, user.id):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Add your resume to begin")
    ctx = context_service.assemble_context(db, user.id)
    row = session_service.new_session(db, user.id, "counselor")
    opener = await generate_opener(ctx)
    await session_for(row.id).add_items([{"role": "assistant", "content": opener}])
    return CounselorState(session_id=row.id, messages=[ChatMessage(role="assistant", content=opener)])


@router.get("/latest", response_model=CounselorState)
async def latest(
    user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> CounselorState:
    row = session_service.latest_session(db, user.id, "counselor")
    if not row:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "No counselor session yet")
    return CounselorState(session_id=row.id, messages=await _history(row.id))


@router.post("/message")
async def message(
    body: CounselorMessageIn,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> StreamingResponse:
    row = session_service.get_session(db, user.id, body.session_id)
    if not row:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Session not found")
    ctx = context_service.assemble_context(db, user.id)

    async def gen() -> AsyncIterator[str]:
        if looks_like_injection(body.message):
            yield f"data: {json.dumps({'delta': REFUSAL})}\n\n"
            yield "data: [DONE]\n\n"
            return
        try:
            async for delta in stream_counselor(body.session_id, ctx, body.message):
                yield f"data: {json.dumps({'delta': delta})}\n\n"
        except Exception as exc:  # noqa: BLE001
            yield f"data: {json.dumps({'error': str(exc)})}\n\n"
            return
        with SessionLocal() as wdb:
            fresh = wdb.get(CounselingSession, body.session_id)
            if fresh:
                fresh.turns = (fresh.turns or 0) + 1
                wdb.add(fresh)
                wdb.commit()
        yield "data: [DONE]\n\n"

    return StreamingResponse(gen(), media_type="text/event-stream")
