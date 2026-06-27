"""FastAPI application entrypoint."""
from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .agents.runtime import configure_groq
from .config import settings
from .database import init_db

logging.basicConfig(level=logging.INFO)


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    configure_groq()
    yield


app = FastAPI(title=settings.app_name, version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_origin_regex=r"http://localhost:\d+",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", tags=["health"])
def health() -> dict:
    return {"status": "ok", "app": settings.app_name}


def register_routers() -> None:
    from .routers import (
        assessment,
        auth,
        counselor,
        discovery,
        interview,
        jobs,
        overview,
        resume,
        roadmap,
    )

    app.include_router(auth.router)
    app.include_router(resume.router)
    app.include_router(discovery.router)
    app.include_router(assessment.router)
    app.include_router(jobs.router)
    app.include_router(interview.router)
    app.include_router(roadmap.router)
    app.include_router(counselor.router)
    app.include_router(overview.router)


register_routers()
