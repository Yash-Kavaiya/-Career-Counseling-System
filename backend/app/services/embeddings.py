"""Local embeddings (fastembed) + numpy cosine — zero-infra vector search.

The single seam for semantic similarity. fastembed downloads a small ONNX model
on first use (no API key). If it is unavailable for any reason, callers fall back
to passing all candidates to the LLM (fine at MVP scale).
"""
from __future__ import annotations

import logging
import threading

import numpy as np

from ..config import settings

logger = logging.getLogger(__name__)

_model = None
_available: bool | None = None
_lock = threading.Lock()


def _get_model():
    global _model, _available
    if _available is False:
        return None
    if _model is None:
        with _lock:
            if _model is None and _available is not False:
                try:
                    from fastembed import TextEmbedding

                    _model = TextEmbedding(model_name=settings.embedding_model)
                    _available = True
                    logger.info("fastembed model loaded: %s", settings.embedding_model)
                except Exception as exc:  # noqa: BLE001
                    logger.warning("fastembed unavailable (%s) — using LLM-only matching", exc)
                    _available = False
    return _model


def available() -> bool:
    _get_model()
    return bool(_available)


def embed_many(texts: list[str]) -> list[list[float]] | None:
    model = _get_model()
    if model is None:
        return None
    return [list(map(float, vec)) for vec in model.embed(texts)]


def embed_one(text: str) -> list[float] | None:
    out = embed_many([text])
    return out[0] if out else None


def cosine_topk(
    query: list[float], items: list[tuple[int, list[float]]], k: int
) -> list[int]:
    """Return the ids of the top-k items by cosine similarity to query."""
    if not items:
        return []
    q = np.asarray(query, dtype=float)
    qn = np.linalg.norm(q) or 1.0
    scored: list[tuple[int, float]] = []
    for idx, vec in items:
        v = np.asarray(vec, dtype=float)
        denom = (np.linalg.norm(v) * qn) or 1.0
        scored.append((idx, float(np.dot(q, v) / denom)))
    scored.sort(key=lambda x: x[1], reverse=True)
    return [idx for idx, _ in scored[:k]]
