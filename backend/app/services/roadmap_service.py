from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models.roadmap import RoadmapRecord
from ..schemas.roadmap import Roadmap


def get_roadmap(db: Session, user_id: int) -> Roadmap | None:
    row = db.scalar(select(RoadmapRecord).where(RoadmapRecord.user_id == user_id))
    return Roadmap.model_validate(row.data) if row else None


def save_roadmap(db: Session, user_id: int, roadmap: Roadmap) -> RoadmapRecord:
    row = db.scalar(select(RoadmapRecord).where(RoadmapRecord.user_id == user_id))
    data = roadmap.model_dump()
    if row:
        row.data = data
    else:
        row = RoadmapRecord(user_id=user_id, data=data)
        db.add(row)
    db.commit()
    db.refresh(row)
    return row


def toggle_milestone(
    db: Session, user_id: int, item_index: int, milestone_index: int, done: bool
) -> Roadmap | None:
    row = db.scalar(select(RoadmapRecord).where(RoadmapRecord.user_id == user_id))
    if not row:
        return None
    data = dict(row.data)
    items = data.get("items", [])
    if 0 <= item_index < len(items):
        milestones = items[item_index].get("milestones", [])
        if 0 <= milestone_index < len(milestones):
            milestones[milestone_index]["done"] = done
            row.data = data
            db.commit()
            db.refresh(row)
    return Roadmap.model_validate(row.data)
