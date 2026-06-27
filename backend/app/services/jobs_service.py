"""Curated-job seeding, semantic candidate selection, and user JD paste."""
from __future__ import annotations

import json
from pathlib import Path

from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from ..models.job import Job
from ..schemas.jobs import JDPasteIn
from . import embeddings

SEED_PATH = Path(__file__).resolve().parent.parent / "seed" / "curated_jobs.json"


def seed_curated(db: Session) -> None:
    if db.scalar(select(Job.id).where(Job.source == "curated")):
        return
    data = json.loads(SEED_PATH.read_text(encoding="utf-8"))
    texts = [
        f"{d['title']} {d.get('company','')} {' '.join(d.get('tech', []))} {d['jd_text']}"
        for d in data
    ]
    vecs = embeddings.embed_many(texts)
    for i, d in enumerate(data):
        db.add(
            Job(
                user_id=None,
                title=d["title"],
                company=d.get("company", ""),
                location=d.get("location", ""),
                remote=d.get("remote", ""),
                salary_band=d.get("salary_band", ""),
                tech=d.get("tech", []),
                jd_text=d["jd_text"],
                embedding=(vecs[i] if vecs else None),
                source="curated",
            )
        )
    db.commit()


def list_jobs(db: Session, user_id: int) -> list[Job]:
    return list(
        db.scalars(
            select(Job).where(or_(Job.user_id.is_(None), Job.user_id == user_id))
        )
    )


def candidate_jobs(db: Session, user_id: int, profile_text: str, k: int = 8) -> list[Job]:
    jobs = list_jobs(db, user_id)
    if len(jobs) <= k or not embeddings.available():
        return jobs
    qv = embeddings.embed_one(profile_text)
    items = [(j.id, j.embedding) for j in jobs if j.embedding]
    if not qv or not items:
        return jobs
    ordered = embeddings.cosine_topk(qv, items, k)
    by_id = {j.id: j for j in jobs}
    picked = [by_id[i] for i in ordered if i in by_id]
    # always include the user's own pasted jobs
    for j in jobs:
        if j.user_id == user_id and j not in picked:
            picked.append(j)
    return picked or jobs


def add_user_job(db: Session, user_id: int, paste: JDPasteIn) -> Job:
    vec = embeddings.embed_one(f"{paste.title} {paste.company} {paste.jd_text}")
    job = Job(
        user_id=user_id,
        title=paste.title,
        company=paste.company,
        location=paste.location,
        remote=paste.remote,
        tech=[],
        jd_text=paste.jd_text,
        embedding=vec,
        source="user",
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    return job
