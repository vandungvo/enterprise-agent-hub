"""AI usage KPIs for leadership: adoption, cost, latency, quality signals.

All aggregation runs in the database (GROUP BY / COUNT DISTINCT), so cost and memory stay flat as the
llm_calls table grows; the (department, created_at) index serves the BU-scoped queries.
"""
from __future__ import annotations

from datetime import timedelta

from fastapi import APIRouter, Depends
from sqlalchemy import case, func, select

from app import hris
from app.access import Principal
from app.access.auth import require_any_role
from app.api.presenters import USAGE_VIEWERS, unit_name
from app.core.db import SessionLocal, utcnow
from app.models import ChatMessage, Conversation, DataAccessLog, LLMCall, PendingAction, ToolCall, User

router = APIRouter(tags=["metrics"])


def _grouped(db, base_filter, key) -> dict:
    rows = db.execute(
        select(key.label("k"), func.count(), func.coalesce(func.sum(LLMCall.output_tokens), 0),
               func.coalesce(func.sum(LLMCall.cost_usd), 0.0), func.avg(LLMCall.latency_ms),
               func.count(func.distinct(LLMCall.user_id)))
        .where(*base_filter).group_by(key)
    ).all()
    return {str(k): {"calls": n, "output_tokens": int(out), "cost_usd": round(float(cost), 4),
                     "avg_latency_ms": round(float(lat or 0)), "active_users": users}
            for k, n, out, cost, lat, users in rows}


@router.get("/metrics")
def metrics(days: int = 30, p: Principal = Depends(require_any_role(*USAGE_VIEWERS))):
    since = utcnow() - timedelta(days=max(1, min(days, 365)))
    # exec of a BU sees that BU; group-level exec / CHRO / platform admin see all
    group_wide = p.is_platform_admin or "chro" in p.roles or hris.GROUP_UNIT in p.role_scopes.get("exec", set())
    bu_filter = None if group_wide else p.bu_code
    calls_filter = [LLMCall.created_at >= since] + ([LLMCall.department == bu_filter] if bu_filter else [])

    with SessionLocal() as db:
        calls, users, cost, cache_read, total_in, latency, refusals = db.execute(
            select(func.count(), func.count(func.distinct(LLMCall.user_id)),
                   func.coalesce(func.sum(LLMCall.cost_usd), 0.0),
                   func.coalesce(func.sum(LLMCall.cache_read_tokens), 0),
                   func.coalesce(func.sum(LLMCall.input_tokens + LLMCall.cache_read_tokens
                                          + LLMCall.cache_write_tokens), 0),
                   func.avg(LLMCall.latency_ms),
                   func.coalesce(func.sum(case((LLMCall.stop_reason == "refusal", 1), else_=0)), 0))
            .where(*calls_filter)
        ).one()
        by_department = _grouped(db, calls_filter, LLMCall.department)
        by_agent = _grouped(db, calls_filter, LLMCall.agent_id)
        by_day = _grouped(db, calls_filter, func.date(LLMCall.created_at))
        tool_rows = db.execute(select(ToolCall.tool, func.count(), func.sum(case((ToolCall.is_error, 1), else_=0)),
                                      func.avg(ToolCall.latency_ms)).where(ToolCall.created_at >= since)
                               .group_by(ToolCall.tool)).all()
        fb = dict(db.execute(select(ChatMessage.feedback, func.count())
                             .where(ChatMessage.role == "assistant", ChatMessage.created_at >= since)
                             .group_by(ChatMessage.feedback)).all())
        approvals = dict(db.execute(select(PendingAction.status, func.count())
                                    .where(PendingAction.created_at >= since).group_by(PendingAction.status)).all())
        denied = db.scalar(select(func.count()).select_from(DataAccessLog)
                           .where(DataAccessLog.created_at >= since, DataAccessLog.allowed.is_(False)))
        conversations = db.scalar(select(func.count()).select_from(Conversation).where(Conversation.created_at >= since))
        accounts = db.scalar(select(func.count()).select_from(User))

    return {
        "scope": unit_name(bu_filter) if bu_filter else "Toàn tập đoàn",
        "totals": {
            "llm_calls": calls, "conversations": conversations, "active_users": users,
            "total_users": accounts, "adoption_rate": round(users / max(accounts, 1), 3),
            "cost_usd": round(float(cost), 4),
            "cache_hit_rate": round(int(cache_read) / max(int(total_in), 1), 3),
            "avg_latency_ms": round(float(latency or 0)),
            "feedback_up": fb.get(1, 0), "feedback_down": fb.get(-1, 0),
            "refusals": int(refusals), "denied_data_access": denied,
        },
        "by_department": {unit_name(k): v for k, v in by_department.items()},
        "by_agent": by_agent,
        "by_day": dict(sorted(by_day.items())),
        "tools": [{"tool": t, "calls": n, "errors": int(e or 0), "avg_latency_ms": round(float(lat or 0))}
                  for t, n, e, lat in tool_rows],
        "approvals": approvals,
    }
