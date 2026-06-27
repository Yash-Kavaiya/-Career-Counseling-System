"""Assemble the user's full journey into one context block for the supervisor.

This is the engine behind "remembers everything": every counselor turn is grounded
in the latest profile, assessment, discovery insights, roadmap progress, and
interview practice.
"""
from __future__ import annotations

from sqlalchemy.orm import Session

from . import assessment_service, profile_service, roadmap_service, session_service
from .profile_text import profile_summary


def assemble_context(db: Session, user_id: int) -> str:
    parts: list[str] = []

    profile = profile_service.get_profile(db, user_id)
    if profile:
        parts.append("PROFILE:\n" + profile_summary(profile))

    a = assessment_service.get_assessment(db, user_id)
    if a:
        parts.append(
            f"ASSESSMENT: target {a.target_role} ({a.level}), readiness {a.readiness_score}/100. "
            f"Strengths: {', '.join(s.title for s in a.strengths)}. "
            f"Gaps: {', '.join(g.title for g in a.gaps)}."
        )

    disc = session_service.latest_session(db, user_id, "discovery")
    if disc and disc.key_insights:
        parts.append(
            "DISCOVERY INSIGHTS:\n" + "\n".join(f"- {i}" for i in disc.key_insights)
        )

    road = roadmap_service.get_roadmap(db, user_id)
    if road:
        done = sum(1 for it in road.items for m in it.milestones if m.done)
        total = sum(len(it.milestones) for it in road.items)
        parts.append(
            f"ROADMAP: {len(road.items)} items, {done}/{total} milestones done. "
            f"Items: {', '.join(it.title for it in road.items)}."
        )

    iv = session_service.latest_session(db, user_id, "interview")
    if iv:
        parts.append(f"INTERVIEW: practiced {iv.turns or 0} question(s) so far.")

    return "\n\n".join(parts) or "No data yet — the candidate has just started."


def has_any(db: Session, user_id: int) -> bool:
    return profile_service.get_profile(db, user_id) is not None
