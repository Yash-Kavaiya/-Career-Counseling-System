from __future__ import annotations

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..agents.discovery_agent import DISCOVERY_TOPICS, session_for
from ..deps import get_current_user, get_db
from ..models.assessment import AssessmentRecord
from ..models.interview import InterviewFeedback
from ..models.job import Job
from ..models.profile import Profile
from ..models.roadmap import RoadmapRecord
from ..models.session import CounselingSession
from ..models.user import User
from ..schemas.counselor import Overview
from ..services import (
    assessment_service,
    profile_service,
    roadmap_service,
    session_service,
)

router = APIRouter(prefix="/api/me", tags=["overview"])


@router.get("/overview", response_model=Overview)
def overview(
    user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> Overview:
    profile = profile_service.get_profile(db, user.id)
    a = assessment_service.get_assessment(db, user.id)
    road = roadmap_service.get_roadmap(db, user.id)
    disc = session_service.latest_session(db, user.id, "discovery")
    iv = session_service.latest_session(db, user.id, "interview")

    done = sum(1 for it in road.items for m in it.milestones if m.done) if road else 0
    total = sum(len(it.milestones) for it in road.items) if road else 0

    return Overview(
        has_profile=profile is not None,
        profile_name=profile.name if profile else None,
        has_assessment=a is not None,
        readiness=a.readiness_score if a else None,
        target_role=a.target_role if a else None,
        has_roadmap=road is not None,
        roadmap_done=done,
        roadmap_total=total,
        discovery_turns=disc.turns if disc else 0,
        discovery_covered=len(disc.covered_topics) if disc else 0,
        discovery_total=len(DISCOVERY_TOPICS),
        latest_insight=(disc.key_insights[-1] if disc and disc.key_insights else None),
        interview_turns=iv.turns if iv else 0,
    )


@router.get("/export")
def export_me(
    user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> dict:
    """Full data export (DPDP/GDPR right to access)."""
    profile = profile_service.get_profile(db, user.id)
    a = assessment_service.get_assessment(db, user.id)
    road = roadmap_service.get_roadmap(db, user.id)
    sessions = db.scalars(
        select(CounselingSession).where(CounselingSession.user_id == user.id)
    ).all()
    sids = [s.id for s in sessions]
    feedback = (
        db.scalars(
            select(InterviewFeedback).where(InterviewFeedback.session_id.in_(sids))
        ).all()
        if sids
        else []
    )
    jobs = db.scalars(select(Job).where(Job.user_id == user.id)).all()
    return {
        "user": {"email": user.email, "full_name": user.full_name},
        "profile": profile.model_dump() if profile else None,
        "assessment": a.model_dump() if a else None,
        "roadmap": road.model_dump() if road else None,
        "sessions": [
            {
                "id": s.id,
                "kind": s.kind,
                "covered_topics": s.covered_topics,
                "key_insights": s.key_insights,
                "turns": s.turns,
            }
            for s in sessions
        ],
        "interview_feedback": [
            {"question": f.question, "answer": f.answer, **f.data} for f in feedback
        ],
        "pasted_jobs": [
            {"title": j.title, "company": j.company, "jd_text": j.jd_text} for j in jobs
        ],
    }


@router.delete("", status_code=status.HTTP_204_NO_CONTENT)
async def delete_me(
    user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> Response:
    """Delete the account and ALL associated data (right to erasure)."""
    sessions = db.scalars(
        select(CounselingSession).where(CounselingSession.user_id == user.id)
    ).all()
    sids = [s.id for s in sessions]
    for sid in sids:  # clear agent conversation memory
        try:
            await session_for(sid).clear_session()
        except Exception:  # noqa: BLE001
            pass
    if sids:
        db.query(InterviewFeedback).filter(
            InterviewFeedback.session_id.in_(sids)
        ).delete(synchronize_session=False)
    for model in (CounselingSession, Profile, AssessmentRecord, RoadmapRecord, Job):
        db.query(model).filter(model.user_id == user.id).delete(synchronize_session=False)
    db.delete(user)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
