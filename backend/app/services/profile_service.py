"""Persistence for the canonical candidate profile (one current per user)."""
from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models.profile import Profile
from ..schemas.profile import CandidateProfile


def get_profile_row(db: Session, user_id: int) -> Profile | None:
    return db.scalar(select(Profile).where(Profile.user_id == user_id))


def get_profile(db: Session, user_id: int) -> CandidateProfile | None:
    row = get_profile_row(db, user_id)
    return CandidateProfile.model_validate(row.data) if row else None


def save_profile(db: Session, user_id: int, profile: CandidateProfile) -> Profile:
    row = get_profile_row(db, user_id)
    data = profile.model_dump()
    if row:
        row.data = data
        row.version += 1
    else:
        row = Profile(user_id=user_id, data=data, version=1)
        db.add(row)
    db.commit()
    db.refresh(row)
    return row
