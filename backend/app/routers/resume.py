from __future__ import annotations

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from ..agents.parser_agent import parse_resume
from ..deps import get_current_user, get_db
from ..models.user import User
from ..schemas.profile import CandidateProfile, ProfileEnvelope
from ..services import profile_service
from ..services.document import extract_resume

router = APIRouter(prefix="/api/resume", tags=["resume"])

MAX_BYTES = 10 * 1024 * 1024  # 10 MB


@router.post("/parse", response_model=ProfileEnvelope)
async def parse(
    file: UploadFile = File(...),
    user: User = Depends(get_current_user),
) -> ProfileEnvelope:
    data = await file.read()
    if not data:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Empty file")
    if len(data) > MAX_BYTES:
        raise HTTPException(status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, "File too large (max 10 MB)")

    content = extract_resume(file.filename or "resume", data)
    if not content.text and not content.images:
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_ENTITY, "Could not read any content from the file"
        )
    try:
        profile = await parse_resume(content)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status.HTTP_502_BAD_GATEWAY, f"Parsing failed: {exc}") from exc
    return ProfileEnvelope(profile=profile, saved=False)


@router.get("/profile", response_model=ProfileEnvelope)
def read_profile(
    user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> ProfileEnvelope:
    row = profile_service.get_profile_row(db, user.id)
    if not row:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "No profile yet")
    return ProfileEnvelope(
        profile=CandidateProfile.model_validate(row.data), version=row.version, saved=True
    )


@router.put("/profile", response_model=ProfileEnvelope)
def write_profile(
    profile: CandidateProfile,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ProfileEnvelope:
    row = profile_service.save_profile(db, user.id, profile)
    return ProfileEnvelope(
        profile=CandidateProfile.model_validate(row.data), version=row.version, saved=True
    )
