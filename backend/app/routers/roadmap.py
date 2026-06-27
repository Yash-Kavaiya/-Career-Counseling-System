from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..agents.roadmap_agent import generate_roadmap
from ..deps import get_current_user, get_db
from ..models.user import User
from ..schemas.roadmap import MilestoneToggle, RoadmapEnvelope
from ..services import assessment_service, profile_service, roadmap_service

router = APIRouter(prefix="/api/roadmap", tags=["roadmap"])


@router.post("/generate", response_model=RoadmapEnvelope)
async def generate(
    user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> RoadmapEnvelope:
    profile = profile_service.get_profile(db, user.id)
    if not profile:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Add and save your resume first")
    assessment = assessment_service.get_assessment(db, user.id)
    if not assessment:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Run your assessment first")
    try:
        roadmap = await generate_roadmap(profile, assessment)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status.HTTP_502_BAD_GATEWAY, f"Roadmap failed: {exc}") from exc
    roadmap_service.save_roadmap(db, user.id, roadmap)
    return RoadmapEnvelope(roadmap=roadmap, saved=True)


@router.get("", response_model=RoadmapEnvelope)
def get(
    user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> RoadmapEnvelope:
    r = roadmap_service.get_roadmap(db, user.id)
    if not r:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "No roadmap yet")
    return RoadmapEnvelope(roadmap=r, saved=True)


@router.patch("/milestone", response_model=RoadmapEnvelope)
def toggle(
    body: MilestoneToggle,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> RoadmapEnvelope:
    r = roadmap_service.toggle_milestone(
        db, user.id, body.item_index, body.milestone_index, body.done
    )
    if not r:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "No roadmap yet")
    return RoadmapEnvelope(roadmap=r, saved=True)
