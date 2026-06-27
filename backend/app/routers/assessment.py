from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..agents.assessor_agent import run_assessment
from ..deps import get_current_user, get_db
from ..models.user import User
from ..schemas.assessment import AssessmentEnvelope
from ..services import assessment_service, profile_service, session_service

router = APIRouter(prefix="/api/assessment", tags=["assessment"])


@router.post("/run", response_model=AssessmentEnvelope)
async def run(
    user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> AssessmentEnvelope:
    profile = profile_service.get_profile(db, user.id)
    if not profile:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Add and save your resume first")
    sess = session_service.latest_session(db, user.id, "discovery")
    insights = list(sess.key_insights or []) if sess else []
    try:
        assessment = await run_assessment(profile, insights)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status.HTTP_502_BAD_GATEWAY, f"Assessment failed: {exc}") from exc
    assessment_service.save_assessment(db, user.id, assessment)
    return AssessmentEnvelope(assessment=assessment, saved=True)


@router.get("", response_model=AssessmentEnvelope)
def get(
    user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> AssessmentEnvelope:
    a = assessment_service.get_assessment(db, user.id)
    if not a:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "No assessment yet")
    return AssessmentEnvelope(assessment=a, saved=True)
