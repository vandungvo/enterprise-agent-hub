"""HTTP API + static web UI."""
from __future__ import annotations

import asyncio
import json
import logging
from contextlib import asynccontextmanager
from datetime import timedelta

from fastapi import Depends, FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from sqlalchemy import case, func, select

from . import hris
from .auth import create_session, current_principal, require_any_role, verify_password
from .chat import ChatError, chat_turn
from .db import (ChatMessage, Conversation, DataAccessLog, Document, LLMCall, PendingAction, SessionLocal, ToolCall,
                 User, utcnow)
from .policy import Principal, policy, principal_for
from .rag import knowledge
from .rag.service import acl_allows
from .llm import effective_model
from .registry import get_platform, reload_platform
from .seed import DEMO_PASSWORD, seed
from .settings import settings
from .tools import REGISTRY

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
log = logging.getLogger("agenthub")
MAX_UPLOAD_BYTES = 20 * 1024 * 1024
USAGE_VIEWERS = ("platform_admin", "exec", "chro")

ROLE_LABELS = {
    "employee": "Nhân viên", "manager": "Quản lý (có cấp dưới)", "unit_head": "Trưởng đơn vị", "ceo": "CEO tập đoàn",
    "exec": "Ban điều hành", "chro": "Giám đốc Nhân sự", "cfo": "Giám đốc Tài chính", "cnb": "C&B",
    "hrbp": "HR Business Partner", "finance": "Kiểm soát tài chính", "it_support": "IT Support",
    "auditor": "Kiểm toán / tuân thủ", "platform_admin": "Quản trị nền tảng",
}


@asynccontextmanager
async def lifespan(_app: FastAPI):
    await asyncio.to_thread(seed)
    yield


app = FastAPI(title="Enterprise Agent Hub", version="0.2.0", lifespan=lifespan)


def unit_name(code: str) -> str:
    return hris.get_org().units.get(code, {}).get("name", code)


def principal_dict(p: Principal) -> dict:
    return {"employee_id": p.employee_id, "email": p.email, "full_name": p.full_name, "title": p.title,
            "level": p.level, "unit_code": p.unit_code, "bu_code": p.bu_code,
            "unit_path": [unit_name(c) for c in p.org.ancestors(p.unit_code)]}


# =========================================================================== auth & identity
class LoginIn(BaseModel):
    email: str
    password: str


@app.get("/api/demo-users")
def demo_users():
    return {"password": DEMO_PASSWORD,
            "users": [{"email": p["email"], "full_name": p["full_name"], "title": p["title"], "key": p["key"]}
                      for p in hris.PERSONAS]}


@app.post("/api/login")
def login(body: LoginIn):
    with SessionLocal() as db:
        user = db.scalar(select(User).where(User.email == body.email.strip().lower()))
    if user is None or not verify_password(body.password, user.password_hash):
        raise HTTPException(401, "Sai email hoặc mật khẩu")
    if principal_for(user.email, user.id) is None:
        raise HTTPException(403, "Tài khoản không còn hiệu lực trong HRIS")
    return {"token": create_session(user)}


def permission_summary(p: Principal) -> list[dict]:
    """Human-readable 'what can I see' per data resource - shown in the UI."""
    out = []
    total = len(p.org.employees)
    for res, spec in policy.resources.items():
        if res == "finance.budget":
            units = policy.unit_scope(p, res)
            scope = "Không" if not units else ("Toàn tập đoàn" if len(units) == len(p.org.units)
                                               else ", ".join(sorted(unit_name(u) for u in units
                                                                     if p.org.units[u]["parent_code"] not in units)))
        else:
            d = policy.scope(p, res)
            ids = d.employee_ids
            if not ids:
                scope = "Không"
            elif ids == {p.employee_id}:
                scope = "Chỉ bản thân"
            elif len(ids) >= total:
                scope = "Toàn tập đoàn"
            else:
                scope = f"Bản thân + {len(ids - {p.employee_id})} người" if p.employee_id in ids else f"{len(ids)} người"
            if d.allowed and res == "compensation.aggregate":
                scope += f" (ẩn nhóm < {d.min_group_size} người)" if d.min_group_size > 1 else " (không ẩn nhóm nhỏ)"
        out.append({"resource": res, "description": spec.get("description", ""),
                    "classification": spec.get("classification", "internal"), "scope": scope})
    return out


@app.get("/api/me")
def me(p: Principal = Depends(current_principal)):
    platform = get_platform()
    return {
        "user": principal_dict(p),
        "company": platform.company,
        "roles": [{"role": r, "label": ROLE_LABELS.get(r, r),
                   "scope": [unit_name(u) for u in sorted(p.role_scopes.get(r, set()))]} for r in sorted(p.roles)],
        "permissions": permission_summary(p),
        "agents": [{"id": a.id, "name": a.name, "role": a.role, "description": a.description}
                   for a in platform.agents_for(p)],
        "knowledge_bases": [{"id": k.id, "name": k.name, "description": k.description,
                             "can_manage": platform.can_manage_kb(k.id, p)} for k in platform.kbs_for(p)],
        "can_view_usage": bool(set(USAGE_VIEWERS) & p.roles),
        "is_platform_admin": p.is_platform_admin,
        "is_auditor": "auditor" in p.roles,
    }


# =========================================================================== chat
class ChatIn(BaseModel):
    message: str
    conversation_id: int | None = None
    agent_id: str | None = None


@app.post("/api/chat")
async def chat(body: ChatIn, p: Principal = Depends(current_principal)):
    if not body.message.strip():
        raise HTTPException(400, "Tin nhắn trống")

    async def stream():
        try:
            async for ev in chat_turn(p, body.message, body.conversation_id, body.agent_id):
                yield f"data: {json.dumps(ev, ensure_ascii=False, default=str)}\n\n"
        except ChatError as exc:
            yield f"data: {json.dumps({'type': 'error', 'text': str(exc)}, ensure_ascii=False)}\n\n"
        except Exception as exc:  # noqa: BLE001
            log.exception("chat failed")
            yield f"data: {json.dumps({'type': 'error', 'text': f'Lỗi hệ thống: {exc}'}, ensure_ascii=False)}\n\n"

    return StreamingResponse(stream(), media_type="text/event-stream",
                             headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})


@app.get("/api/conversations")
def list_conversations(p: Principal = Depends(current_principal)):
    with SessionLocal() as db:
        rows = db.scalars(select(Conversation).where(Conversation.user_id == p.user_id)
                          .order_by(Conversation.updated_at.desc()).limit(100)).all()
    return [{"id": c.id, "title": c.title, "agent_id": c.agent_id, "sensitive": c.sensitive,
             "updated_at": c.updated_at} for c in rows]


def _own_conversation(db, conv_id: int, p: Principal) -> Conversation:
    conv = db.get(Conversation, conv_id)
    if conv is None or conv.user_id != p.user_id:
        raise HTTPException(404, "Không tìm thấy")
    return conv


@app.get("/api/conversations/{conv_id}")
def get_conversation(conv_id: int, p: Principal = Depends(current_principal)):
    with SessionLocal() as db:
        conv = _own_conversation(db, conv_id, p)
        msgs = db.scalars(select(ChatMessage).where(ChatMessage.conversation_id == conv_id)
                          .order_by(ChatMessage.id)).all()
    return {"id": conv.id, "title": conv.title, "agent_id": conv.agent_id, "sensitive": conv.sensitive,
            "messages": [{"id": m.id, "role": m.role, "content": m.content, "sources": m.sources,
                          "trace": m.trace, "feedback": m.feedback} for m in msgs]}


@app.delete("/api/conversations/{conv_id}")
def delete_conversation(conv_id: int, p: Principal = Depends(current_principal)):
    with SessionLocal() as db:
        conv = _own_conversation(db, conv_id, p)
        db.query(ChatMessage).filter(ChatMessage.conversation_id == conv_id).delete()
        db.delete(conv)
        db.commit()
    return {"ok": True}


class FeedbackIn(BaseModel):
    value: int
    comment: str | None = None


@app.post("/api/messages/{msg_id}/feedback")
def feedback(msg_id: int, body: FeedbackIn, p: Principal = Depends(current_principal)):
    with SessionLocal() as db:
        msg = db.get(ChatMessage, msg_id)
        if msg is None:
            raise HTTPException(404, "Không tìm thấy")
        _own_conversation(db, msg.conversation_id, p)
        msg.feedback = 1 if body.value > 0 else -1
        msg.feedback_comment = body.comment
        db.commit()
    return {"ok": True}


# =========================================================================== knowledge
@app.get("/api/kbs/{kb_id}/documents")
def list_documents(kb_id: str, p: Principal = Depends(current_principal)):
    platform = get_platform()
    if kb_id not in {k.id for k in platform.kbs_for(p)}:
        raise HTTPException(403, "Không có quyền")
    manager = platform.can_manage_kb(kb_id, p)
    with SessionLocal() as db:
        docs = db.scalars(select(Document).where(Document.kb_id == kb_id).order_by(Document.created_at.desc())).all()
    # Documents the user cannot read are invisible (not even their titles), except to KB managers.
    return [{"id": d.id, "title": d.title, "filename": d.filename, "num_chunks": d.num_chunks,
             "classification": d.classification, "acl": d.acl, "created_at": d.created_at}
            for d in docs if manager or acl_allows(d.acl, p)]


@app.post("/api/kbs/{kb_id}/documents")
async def upload_document(kb_id: str, file: UploadFile = File(...), title: str | None = Form(None),
                          classification: str = Form("internal"), roles: str | None = Form(None),
                          min_level: int | None = Form(None), p: Principal = Depends(current_principal)):
    if not get_platform().can_manage_kb(kb_id, p):
        raise HTTPException(403, "Bạn không có quyền quản lý knowledge base này")
    if classification not in ("internal", "confidential", "restricted"):
        raise HTTPException(400, "classification không hợp lệ")
    data = await file.read()
    if len(data) > MAX_UPLOAD_BYTES:
        raise HTTPException(413, "File quá lớn (tối đa 20MB)")
    acl = {}
    if roles:
        acl["roles"] = [r.strip() for r in roles.split(",") if r.strip()]
    if min_level:
        acl["min_level"] = min_level
    try:
        doc = await asyncio.to_thread(knowledge.ingest, kb_id, file.filename or "document.txt", data, title or None,
                                      p.user_id, classification, acl)
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc
    return {"id": doc.id, "title": doc.title, "num_chunks": doc.num_chunks}


@app.delete("/api/documents/{doc_id}")
def delete_document(doc_id: int, p: Principal = Depends(current_principal)):
    with SessionLocal() as db:
        doc = db.get(Document, doc_id)
    if doc is None:
        raise HTTPException(404, "Không tìm thấy")
    if not get_platform().can_manage_kb(doc.kb_id, p):
        raise HTTPException(403, "Không có quyền")
    knowledge.delete_document(doc_id)
    return {"ok": True}


class SearchIn(BaseModel):
    query: str
    kb_ids: list[str] | None = None
    top_k: int = 5


@app.post("/api/kbs/search")
def search(body: SearchIn, p: Principal = Depends(current_principal)):
    allowed = [k.id for k in get_platform().kbs_for(p)]
    kb_ids = [k for k in (body.kb_ids or allowed) if k in allowed]
    return knowledge.search(body.query, kb_ids, max(1, min(body.top_k, 20)), principal=p)


# =========================================================================== approvals (HITL)
def _action_dict(a: PendingAction) -> dict:
    org = hris.get_org()
    name = lambda i: org.employees.get(i, {}).get("full_name") if i else None  # noqa: E731
    return {"id": a.id, "tool": a.tool, "summary": a.summary, "payload": a.payload, "status": a.status,
            "requested_by": a.requester_name or name(a.requested_by), "requested_by_id": a.requested_by,
            "approvers": [name(i) for i in a.approver_ids or []], "decided_by": name(a.decided_by),
            "decision_note": a.decision_note, "result": a.result, "created_at": a.created_at,
            "decided_at": a.decided_at}


@app.get("/api/approvals")
def list_approvals(scope: str = "mine", p: Principal = Depends(current_principal)):
    with SessionLocal() as db:
        rows = db.scalars(select(PendingAction).order_by(PendingAction.id.desc()).limit(300)).all()
    if scope == "review":
        rows = [a for a in rows if p.employee_id in (a.approver_ids or [])]
    else:
        rows = [a for a in rows if a.requested_by == p.employee_id]
    return [_action_dict(a) for a in rows]


class DecisionIn(BaseModel):
    approve: bool
    note: str | None = None


@app.post("/api/approvals/{action_id}/decision")
async def decide(action_id: int, body: DecisionIn, p: Principal = Depends(current_principal)):
    with SessionLocal() as db:
        action = db.get(PendingAction, action_id)
        if action is None:
            raise HTTPException(404, "Không tìm thấy")
        if p.employee_id not in (action.approver_ids or []):
            raise HTTPException(403, "Bạn không phải người phê duyệt của yêu cầu này")
        if action.status != "pending":
            raise HTTPException(409, f"Yêu cầu đã được xử lý ({action.status})")
        # Claim first so a concurrent decision cannot execute it twice.
        action.status, action.decided_by, action.decided_at, action.decision_note = "processing", p.employee_id, utcnow(), body.note
        db.commit()
        requester_email = hris.get_org().employees[action.requested_by]["email"]

    status, result = "rejected", "Đã từ chối"
    if body.approve:
        requester = principal_for(requester_email, 0)
        try:
            if requester is None:
                raise RuntimeError("Người yêu cầu không còn hiệu lực trong HRIS")
            result = await asyncio.to_thread(REGISTRY[action.tool].execute, action.payload, requester)
            status = "executed"
        except Exception as exc:  # noqa: BLE001
            status, result = "failed", f"Lỗi khi thực hiện: {exc}"
    with SessionLocal() as db:
        action = db.get(PendingAction, action_id)
        action.status, action.result = status, result
        db.commit()
    return {"status": status, "result": result}


# =========================================================================== data-access transparency & audit
def _log_dict(r: DataAccessLog) -> dict:
    org = hris.get_org()
    return {"id": r.id, "created_at": r.created_at, "actor": r.actor_name, "resource": r.resource,
            "classification": r.classification,
            "target": org.employees.get(r.target_employee_id, {}).get("full_name") if r.target_employee_id else None,
            "scope": r.scope, "allowed": r.allowed, "audit": r.audit}


@app.get("/api/my-data-access")
def my_data_access(p: Principal = Depends(current_principal)):
    """Who accessed MY confidential / restricted data (transparency for every employee)."""
    with SessionLocal() as db:
        rows = db.scalars(select(DataAccessLog).where(DataAccessLog.target_employee_id == p.employee_id,
                                                      DataAccessLog.actor_employee_id != p.employee_id,
                                                      DataAccessLog.allowed.is_(True))
                          .order_by(DataAccessLog.id.desc()).limit(100)).all()
    return [_log_dict(r) for r in rows]


@app.get("/api/audit/data-access")
def audit_data_access(denied_only: bool = False, p: Principal = Depends(require_any_role("auditor"))):
    with SessionLocal() as db:
        q = select(DataAccessLog).order_by(DataAccessLog.id.desc()).limit(300)
        if denied_only:
            q = q.where(DataAccessLog.allowed.is_(False))
        rows = db.scalars(q).all()
    return [_log_dict(r) for r in rows]


# =========================================================================== usage KPIs
@app.get("/api/metrics")
def metrics(days: int = 30, p: Principal = Depends(require_any_role(*USAGE_VIEWERS))):
    since = utcnow() - timedelta(days=max(1, min(days, 365)))
    # exec of a BU sees that BU; group-level exec / CHRO / platform admin see all
    group_wide = p.is_platform_admin or "chro" in p.roles or hris.GROUP_UNIT in p.role_scopes.get("exec", set())
    bu_filter = None if group_wide else p.bu_code
    with SessionLocal() as db:
        lq = select(LLMCall).where(LLMCall.created_at >= since)
        if bu_filter:
            lq = lq.where(LLMCall.department == bu_filter)
        calls = db.scalars(lq).all()
        user_ids = {c.user_id for c in calls}
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

    def agg(key):
        out: dict = {}
        for c in calls:
            o = out.setdefault(key(c), {"calls": 0, "output_tokens": 0, "cost_usd": 0.0, "latency_ms": 0, "users": set()})
            o["calls"] += 1
            o["output_tokens"] += c.output_tokens
            o["cost_usd"] += c.cost_usd
            o["latency_ms"] += c.latency_ms
            o["users"].add(c.user_id)
        for o in out.values():
            o["avg_latency_ms"] = round(o.pop("latency_ms") / max(o["calls"], 1))
            o["active_users"] = len(o.pop("users"))
            o["cost_usd"] = round(o["cost_usd"], 4)
        return out

    total_in = sum(c.input_tokens + c.cache_read_tokens + c.cache_write_tokens for c in calls)
    return {
        "scope": unit_name(bu_filter) if bu_filter else "Toàn tập đoàn",
        "totals": {
            "llm_calls": len(calls), "conversations": conversations, "active_users": len(user_ids),
            "total_users": accounts, "adoption_rate": round(len(user_ids) / max(accounts, 1), 3),
            "cost_usd": round(sum(c.cost_usd for c in calls), 4),
            "cache_hit_rate": round(sum(c.cache_read_tokens for c in calls) / max(total_in, 1), 3),
            "avg_latency_ms": round(sum(c.latency_ms for c in calls) / max(len(calls), 1)),
            "feedback_up": fb.get(1, 0), "feedback_down": fb.get(-1, 0),
            "refusals": sum(1 for c in calls if c.stop_reason == "refusal"), "denied_data_access": denied,
        },
        "by_department": {unit_name(k): v for k, v in agg(lambda c: c.department).items()},
        "by_agent": agg(lambda c: c.agent_id),
        "by_day": agg(lambda c: c.created_at.date().isoformat()),
        "tools": [{"tool": t, "calls": n, "errors": int(e or 0), "avg_latency_ms": round(lat or 0)}
                  for t, n, e, lat in tool_rows],
        "approvals": approvals,
    }


# =========================================================================== platform admin
@app.get("/api/admin/agents")
def admin_agents(_: Principal = Depends(require_any_role("platform_admin", "auditor"))):
    return [{"id": a.id, "name": a.name, "role": a.role, "model": effective_model(a.model), "effort": a.effort,
             "description": a.description, "tools": a.tools, "knowledge_bases": a.knowledge_bases,
             "access": {"roles": a.access.roles, "min_level": a.access.min_level},
             "approval": {t: REGISTRY[t].needs_approval(a) for t in a.tools if t in REGISTRY and REGISTRY[t].execute},
             "system_prompt": a.system_prompt} for a in get_platform().agents.values()]


@app.get("/api/admin/policies")
def admin_policies(_: Principal = Depends(require_any_role("platform_admin", "auditor", "chro"))):
    return policy.resources


@app.post("/api/admin/reload")
def admin_reload(_: Principal = Depends(require_any_role("platform_admin"))):
    try:
        platform = reload_platform()
        policy.reload()
        hris.reset_org_cache()
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(400, f"Cấu hình lỗi: {exc}") from exc
    return {"agents": len(platform.agents), "knowledge_bases": len(platform.knowledge_bases),
            "resources": len(policy.resources)}


@app.get("/api/admin/audit")
def admin_audit(limit: int = 100, _: Principal = Depends(require_any_role("platform_admin", "auditor"))):
    with SessionLocal() as db:
        rows = db.scalars(select(ToolCall).order_by(ToolCall.id.desc()).limit(min(limit, 500))).all()
        emails = {u.id: u.email for u in db.scalars(select(User)).all()}
    return [{"id": t.id, "created_at": t.created_at, "user": emails.get(t.user_id, "?"), "agent_id": t.agent_id,
             "tool": t.tool, "input": t.input, "output_preview": t.output_preview[:300], "is_error": t.is_error,
             "latency_ms": t.latency_ms} for t in rows]


# =========================================================================== static UI
app.mount("/static", StaticFiles(directory=settings.static_dir), name="static")


@app.get("/")
def index():
    return FileResponse(settings.static_dir / "index.html")
