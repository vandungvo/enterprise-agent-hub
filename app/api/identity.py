"""Login, current identity and 'what can I see' summary."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select

from app import hris
from app.access import Principal, policy, principal_for
from app.access.auth import (
    clear_login_failures,
    create_session,
    current_principal,
    login_throttled,
    record_login_failure,
    verify_password,
)
from app.agents.registry import get_platform
from app.api.presenters import ROLE_LABELS, USAGE_VIEWERS, principal_dict, unit_name
from app.bootstrap import DEMO_PASSWORD
from app.core.db import SessionLocal
from app.models import User

router = APIRouter(tags=["identity"])


class LoginIn(BaseModel):
    email: str
    password: str


@router.get("/demo-users")
def demo_users():
    return {"password": DEMO_PASSWORD,
            "users": [{"email": p["email"], "full_name": p["full_name"], "title": p["title"], "key": p["key"]}
                      for p in hris.PERSONAS]}


@router.post("/login")
def login(body: LoginIn):
    email = body.email.strip().lower()[:200]
    if login_throttled(email):
        raise HTTPException(429, "Đăng nhập sai quá nhiều lần, vui lòng thử lại sau ít phút",
                            headers={"Retry-After": "300"})
    with SessionLocal() as db:
        user = db.scalar(select(User).where(User.email == email))
    if user is None or not verify_password(body.password, user.password_hash):
        record_login_failure(email)
        raise HTTPException(401, "Sai email hoặc mật khẩu")
    clear_login_failures(email)
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


@router.get("/me")
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
