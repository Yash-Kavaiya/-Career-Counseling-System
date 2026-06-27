from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models.assessment import AssessmentRecord
from ..schemas.assessment import Assessment


def get_assessment(db: Session, user_id: int) -> Assessment | None:
    row = db.scalar(select(AssessmentRecord).where(AssessmentRecord.user_id == user_id))
    return Assessment.model_validate(row.data) if row else None


def save_assessment(db: Session, user_id: int, assessment: Assessment) -> AssessmentRecord:
    row = db.scalar(select(AssessmentRecord).where(AssessmentRecord.user_id == user_id))
    data = assessment.model_dump()
    if row:
        row.data = data
    else:
        row = AssessmentRecord(user_id=user_id, data=data)
        db.add(row)
    db.commit()
    db.refresh(row)
    return row
