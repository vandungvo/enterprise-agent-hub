"""Liveness / readiness probe for load balancers and uptime monitors."""
from __future__ import annotations

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.core.db import engine, ping

router = APIRouter(tags=["health"])


@router.get("/health")
def health():
    try:
        ok = ping()
    except Exception:
        ok = False
    body = {"status": "ok" if ok else "degraded", "database": engine.dialect.name, "database_ok": ok}
    return JSONResponse(body, status_code=200 if ok else 503)
