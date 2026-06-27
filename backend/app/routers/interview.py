from __future__ import annotations

import json
from collections.abc import AsyncIterator

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..agents.discovery_agent import session_for
from ..agents.interview_agent import (
    evaluate_answer,
    generate_first_question,
    stream_interviewer,
)
from ..database import SessionLocal
from ..deps import get_current_user, get_db
from ..models.interview import InterviewFeedback
from ..models.session import CounselingSession
from ..models.user import User
from ..schemas.interview import FeedbackItem, InterviewMessageIn, InterviewState
from ..schemas.profile import CandidateProfile
from ..services import assessment_service, profile_service, session_service
from .discovery import _history

router = APIRouter(prefix="/api/interview", tags=["interview"])


def _target_and_focus(db: Session, user_id: int, profile: CandidateProfile | None) -> tuple[str, str]:
    a = assessment_service.get_assessment(db, user_id)
    if a:
        focus = ", ".join(g.title for g in a.gaps[:3]) or "system design and core stack depth"
        return f"{a.target_role} ({a.level})", focus
    if profile and profile.preferences.target_roles:
        return profile.preferences.target_roles[0], "system design, your core stack, and STAR stories"
    return "Software Engineer", "system design, your core stack, and behavioural (STAR) stories"


def _feedbacks(db: Session, session_id: str) -> list[FeedbackItem]:
    rows = (
        db.scalars(
            select(InterviewFeedback)
            .where(InterviewFeedback.session_id == session_id)
            .order_by(InterviewFeedback.id)
        )
    ).all()
    items: list[FeedbackItem] = []
    for r in rows:
        d = dict(r.data)
        items.append(
            FeedbackItem(
                question=r.question,
                answer=r.answer,
                overall=d["overall"],
                scores=d["scores"],
                strengths=d["strengths"],
                improvements=d["improvements"],
                better_answer=d["better_answer"],
            )
        )
    return items


def _readiness(feedbacks: list[FeedbackItem]) -> int:
    if not feedbacks:
        return 0
    return round(sum(f.overall for f in feedbacks) / len(feedbacks) * 10)


async def _state(db: Session, row: CounselingSession, profile: CandidateProfile | None) -> InterviewState:
    role, _ = _target_and_focus(db, row.user_id, profile)
    fbs = _feedbacks(db, row.id)
    return InterviewState(
        session_id=row.id,
        target_role=role,
        messages=await _history(row.id),
        feedbacks=fbs,
        readiness=_readiness(fbs),
        turns=row.turns or 0,
    )


@router.post("/start", response_model=InterviewState)
async def start(
    user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> InterviewState:
    profile = profile_service.get_profile(db, user.id)
    if not profile:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Add and save your resume first")
    role, focus = _target_and_focus(db, user.id, profile)
    row = session_service.new_session(db, user.id, "interview")
    question = await generate_first_question(profile, role, focus)
    await session_for(row.id).add_items([{"role": "assistant", "content": question}])
    return await _state(db, row, profile)


@router.get("/latest", response_model=InterviewState)
async def latest(
    user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> InterviewState:
    row = session_service.latest_session(db, user.id, "interview")
    if not row:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "No interview yet")
    return await _state(db, row, profile_service.get_profile(db, user.id))


@router.post("/message")
async def message(
    body: InterviewMessageIn,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> StreamingResponse:
    row = session_service.get_session(db, user.id, body.session_id)
    if not row:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Session not found")
    profile = profile_service.get_profile(db, user.id)
    role, focus = _target_and_focus(db, user.id, profile)
    history = await _history(body.session_id)
    question = next((m.content for m in reversed(history) if m.role == "assistant"), "")

    async def gen() -> AsyncIterator[str]:
        full = ""
        try:
            async for delta in stream_interviewer(
                body.session_id, profile, role, focus, body.message
            ):
                full += delta
                yield f"data: {json.dumps({'delta': delta})}\n\n"
        except Exception as exc:  # noqa: BLE001
            yield f"data: {json.dumps({'error': str(exc)})}\n\n"
            return

        try:
            fb = await evaluate_answer(question, body.message)
            with SessionLocal() as wdb:
                wdb.add(
                    InterviewFeedback(
                        session_id=body.session_id,
                        question=question,
                        answer=body.message,
                        data=fb.model_dump(),
                    )
                )
                fresh = wdb.get(CounselingSession, body.session_id)
                if fresh:
                    fresh.turns = (fresh.turns or 0) + 1
                    wdb.add(fresh)
                wdb.commit()
                fbs = _feedbacks(wdb, body.session_id)
            payload = {
                "done": True,
                "feedback": fb.model_dump(),
                "readiness": _readiness(fbs),
                "turns": len(fbs),
            }
            yield f"data: {json.dumps(payload)}\n\n"
        except Exception:  # noqa: BLE001 - evaluation is best-effort
            yield f"data: {json.dumps({'done': True})}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(gen(), media_type="text/event-stream")
