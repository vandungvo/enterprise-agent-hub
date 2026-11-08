"""Data-access transparency (every employee) and audit trail (auditors)."""
from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import select

from app.access import Principal
from app.access.auth import current_principal, require_any_role
from app.api.presenters import employee_name
from app.core.db import SessionLocal
from app.models import DataAccessLog

router = APIRouter(tags=["audit"])


def _log_dict(r: DataAccessLog) -> dict:
    return {"id": r.id, "created_at": r.created_at, "actor": r.actor_name, "resource": r.resource,
            "classification": r.classification, "target": employee_name(r.target_employee_id),
            "scope": r.scope, "allowed": r.allowed, "audit": r.audit}


@router.get("/my-data-access")
def my_data_access(p: Principal = Depends(current_principal)):
    """Who accessed MY confidential / restricted data."""
    with SessionLocal() as db:
        rows = db.scalars(select(DataAccessLog).where(DataAccessLog.target_employee_id == p.employee_id,
                                                      DataAccessLog.actor_employee_id != p.employee_id,
                                                      DataAccessLog.allowed.is_(True))
                          .order_by(DataAccessLog.id.desc()).limit(100)).all()
    return [_log_dict(r) for r in rows]


@router.get("/audit/data-access")
def audit_data_access(denied_only: bool = False, p: Principal = Depends(require_any_role("auditor"))):
    with SessionLocal() as db:
        q = select(DataAccessLog).order_by(DataAccessLog.id.desc()).limit(300)
        if denied_only:
            q = q.where(DataAccessLog.allowed.is_(False))
        rows = db.scalars(q).all()
    return [_log_dict(r) for r in rows]
