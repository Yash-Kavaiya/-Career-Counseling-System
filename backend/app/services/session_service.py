"""Create/lookup counseling sessions and update their structured state."""
from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models.session import CounselingSession


def new_session(db: Session, user_id: int, kind: str = "discovery") -> CounselingSession:
    sid = f"{kind[:4]}_{user_id}_{uuid.uuid4().hex[:8]}"
    row = CounselingSession(id=sid, user_id=user_id, kind=kind)
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def get_session(db: Session, user_id: int, session_id: str) -> CounselingSession | None:
    row = db.get(CounselingSession, session_id)
    if row and row.user_id == user_id:
        return row
    return None


def latest_session(
    db: Session, user_id: int, kind: str = "discovery"
) -> CounselingSession | None:
    return db.scalar(
        select(CounselingSession)
        .where(CounselingSession.user_id == user_id, CounselingSession.kind == kind)
        .order_by(CounselingSession.last_activity.desc())
    )


def apply_coverage(
    db: Session,
    row: CounselingSession,
    *,
    newly_covered: list[str],
    insights: list[str],
    pending: list[str],
) -> CounselingSession:
    covered = list(dict.fromkeys([*row.covered_topics, *newly_covered]))
    merged_insights = list(dict.fromkeys([*row.key_insights, *insights]))
    row.covered_topics = covered
    row.key_insights = merged_insights
    row.pending_questions = pending
    row.turns = (row.turns or 0) + 1
    db.add(row)
    db.commit()
    db.refresh(row)
    return row
