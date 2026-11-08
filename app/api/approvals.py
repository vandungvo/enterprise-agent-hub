"""Human-in-the-loop approvals for side-effecting tool calls."""
from __future__ import annotations

from typing import Literal

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select, update

from app import hris
from app.access import Principal, principal_for
from app.access.auth import current_principal
from app.api.presenters import employee_name
from app.core.db import SessionLocal, utcnow
from app.models import PendingAction, PendingActionApprover
from app.tools import REGISTRY

router = APIRouter(tags=["approvals"])


class DecisionIn(BaseModel):
    approve: bool
    note: str | None = None


def _action_dict(a: PendingAction) -> dict:
    return {"id": a.id, "tool": a.tool, "summary": a.summary, "payload": a.payload, "status": a.status,
            "requested_by": a.requester_name or employee_name(a.requested_by), "requested_by_id": a.requested_by,
            "approvers": [employee_name(i) for i in a.approver_ids or []], "decided_by": employee_name(a.decided_by),
            "decision_note": a.decision_note, "result": a.result, "created_at": a.created_at,
            "decided_at": a.decided_at}


@router.get("/approvals")
def list_approvals(scope: Literal["mine", "review"] = "mine", p: Principal = Depends(current_principal)):
    with SessionLocal() as db:
        q = select(PendingAction).order_by(PendingAction.id.desc()).limit(300)
        if scope == "mine":
            q = q.where(PendingAction.requested_by == p.employee_id)
        else:  # indexed lookup on the normalized approver table
            q = (q.join(PendingActionApprover, PendingActionApprover.action_id == PendingAction.id)
                 .where(PendingActionApprover.employee_id == p.employee_id))
        rows = db.scalars(q).all()
    return [_action_dict(a) for a in rows]


@router.post("/approvals/{action_id}/decision")
def decide(action_id: int, body: DecisionIn, p: Principal = Depends(current_principal)):
    with SessionLocal() as db:
        action = db.get(PendingAction, action_id)
        if action is None:
            raise HTTPException(404, "Không tìm thấy")
        if p.employee_id not in (action.approver_ids or []):
            raise HTTPException(403, "Bạn không phải người phê duyệt của yêu cầu này")
        # Atomic claim (compare-and-set on status): two approvers - possibly on two server instances -
        # deciding at the same time cannot both execute the action.
        claimed = db.execute(
            update(PendingAction).where(PendingAction.id == action_id, PendingAction.status == "pending")
            .values(status="processing", decided_by=p.employee_id, decided_at=utcnow(), decision_note=body.note)
        ).rowcount
        db.commit()
        if not claimed:
            db.refresh(action)
            raise HTTPException(409, f"Yêu cầu đã được xử lý ({action.status})")
        tool, payload, requested_by = action.tool, action.payload, action.requested_by

    status, result = "rejected", "Đã từ chối"
    if body.approve:
        requester_email = hris.get_org().employees.get(requested_by, {}).get("email")
        requester = principal_for(requester_email, 0) if requester_email else None
        try:
            if requester is None:
                raise RuntimeError("Người yêu cầu không còn hiệu lực trong HRIS")
            result = REGISTRY[tool].execute(payload, requester)  # sync endpoint: already off the event loop
            status = "executed"
        except Exception as exc:
            status, result = "failed", f"Lỗi khi thực hiện: {exc}"
    with SessionLocal() as db:
        db.execute(update(PendingAction).where(PendingAction.id == action_id).values(status=status, result=result))
        db.commit()
    return {"status": status, "result": result}
