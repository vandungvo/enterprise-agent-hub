"""Platform administration: agent / policy inspection, config hot-reload, operational audit."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select

from app import hris
from app.access import Principal, policy
from app.access.auth import require_any_role
from app.agents.registry import get_platform, reload_platform
from app.core.db import SessionLocal
from app.llm import effective_model
from app.models import ToolCall, User
from app.tools import REGISTRY

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/agents")
def admin_agents(_: Principal = Depends(require_any_role("platform_admin", "auditor"))):
    return [{"id": a.id, "name": a.name, "role": a.role, "model": effective_model(a.model), "effort": a.effort,
             "description": a.description, "tools": a.tools, "knowledge_bases": a.knowledge_bases,
             "access": {"roles": a.access.roles, "min_level": a.access.min_level},
             "approval": {t: REGISTRY[t].needs_approval(a) for t in a.tools if t in REGISTRY and REGISTRY[t].execute},
             "system_prompt": a.system_prompt} for a in get_platform().agents.values()]


@router.get("/policies")
def admin_policies(_: Principal = Depends(require_any_role("platform_admin", "auditor", "chro"))):
    return policy.resources


@router.post("/reload")
def admin_reload(_: Principal = Depends(require_any_role("platform_admin"))):
    """Re-read platform.yaml / policies.yaml on THIS process. On multi-instance hosts, redeploy instead."""
    try:
        platform = reload_platform()
        policy.reload()
        hris.reset_org_cache()
    except Exception as exc:
        raise HTTPException(400, f"Cấu hình lỗi: {exc}") from exc
    return {"agents": len(platform.agents), "knowledge_bases": len(platform.knowledge_bases),
            "resources": len(policy.resources)}


@router.get("/audit")
def admin_audit(limit: int = 100, _: Principal = Depends(require_any_role("platform_admin", "auditor"))):
    with SessionLocal() as db:
        rows = db.scalars(select(ToolCall).order_by(ToolCall.id.desc()).limit(max(1, min(limit, 500)))).all()
        user_ids = {t.user_id for t in rows if t.user_id}
        emails = dict(db.execute(select(User.id, User.email).where(User.id.in_(user_ids))).all()) if user_ids else {}
    return [{"id": t.id, "created_at": t.created_at, "user": emails.get(t.user_id, "?"), "agent_id": t.agent_id,
             "tool": t.tool, "input": t.input, "output_preview": t.output_preview[:300], "is_error": t.is_error,
             "latency_ms": t.latency_ms} for t in rows]
