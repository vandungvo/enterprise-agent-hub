"""Internal endpoints for schedulers (Vercel Cron, Kubernetes CronJob...). Not used by the UI.

Protected by CRON_SECRET: callers send `Authorization: Bearer <CRON_SECRET>` (Vercel Cron does this
automatically when the project has a CRON_SECRET variable). Without CRON_SECRET the endpoints are disabled.
"""
from __future__ import annotations

import hmac
import logging
from datetime import timedelta

from fastapi import APIRouter, Header, HTTPException
from sqlalchemy import delete

from app.agents.conversation import purge_expired_conversations
from app.core.db import SessionLocal, utcnow
from app.core.settings import settings
from app.models import LoginFailure

log = logging.getLogger("agenthub.maintenance")
router = APIRouter(prefix="/internal", tags=["internal"], include_in_schema=False)


def _authorize(authorization: str | None) -> None:
    if not settings.cron_secret:
        raise HTTPException(404, "Not found")
    expected = f"Bearer {settings.cron_secret}"
    if not authorization or not hmac.compare_digest(authorization, expected):
        raise HTTPException(401, "Unauthorized")


@router.get("/maintenance")
def maintenance(authorization: str | None = Header(default=None)):
    """Daily housekeeping: retention purge of sensitive conversations, prune old login-failure records."""
    _authorize(authorization)
    purged = purge_expired_conversations()
    with SessionLocal() as db:
        pruned = db.execute(delete(LoginFailure).where(LoginFailure.created_at < utcnow() - timedelta(days=1))).rowcount
        db.commit()
    log.info("maintenance: purged %d sensitive conversations, pruned %d login failures", purged, pruned)
    return {"purged_conversations": purged, "pruned_login_failures": pruned}
