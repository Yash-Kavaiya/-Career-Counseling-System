from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..agents.jobmatch_agent import match_jobs
from ..deps import get_current_user, get_db
from ..models.user import User
from ..schemas.jobs import JDPasteIn, JobOut, MatchView
from ..services import assessment_service, jobs_service, profile_service
from ..services.profile_text import profile_summary

router = APIRouter(prefix="/api/jobs", tags=["jobs"])


@router.get("", response_model=list[JobOut])
def list_jobs(
    user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> list[JobOut]:
    jobs_service.seed_curated(db)
    return [JobOut.model_validate(j) for j in jobs_service.list_jobs(db, user.id)]


@router.post("/paste", response_model=JobOut)
def paste(
    body: JDPasteIn,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> JobOut:
    if not body.jd_text.strip():
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Job description is empty")
    return JobOut.model_validate(jobs_service.add_user_job(db, user.id, body))


@router.get("/match", response_model=list[MatchView])
async def match(
    user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> list[MatchView]:
    profile = profile_service.get_profile(db, user.id)
    if not profile:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Add and save your resume first")
    jobs_service.seed_curated(db)
    assessment = assessment_service.get_assessment(db, user.id)
    candidates = jobs_service.candidate_jobs(db, user.id, profile_summary(profile))
    if not candidates:
        return []
    try:
        result = await match_jobs(profile, assessment, candidates)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status.HTTP_502_BAD_GATEWAY, f"Matching failed: {exc}") from exc

    by_id = {j.id: j for j in candidates}
    views: list[MatchView] = []
    for m in result.matches:
        job = by_id.get(m.job_id)
        if not job:
            continue
        views.append(
            MatchView(
                job=JobOut.model_validate(job),
                fit_score=m.fit_score,
                reasons=m.reasons,
                missing_pieces=m.missing_pieces,
                talking_points=m.talking_points,
            )
        )
    views.sort(key=lambda v: v.fit_score, reverse=True)
    return views
