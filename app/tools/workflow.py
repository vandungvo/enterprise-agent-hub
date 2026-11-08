"""Workflow tools with side effects: expense claims, IT tickets (routed through approvals)."""
from __future__ import annotations

import json
from datetime import date, datetime
from typing import Literal

from pydantic import Field

from .. import hris
from ..policy import Principal, log_access, policy
from .base import ToolContext, ToolDef, ToolInput, register

EXPENSE_MANAGER_LIMIT = 20_000_000  # above this, the BU head approves (demo approval matrix)


# --------------------------------------------------------------------------- expense claims
class ExpenseInput(ToolInput):
    amount: int = Field(gt=0, description="Số tiền VND")
    category: Literal["travel", "accommodation", "meal_client", "training", "equipment", "other"]
    expense_date: str = Field(description="YYYY-MM-DD")
    description: str


def _validate_expense(ctx: ToolContext, inp: ExpenseInput) -> None:
    d = date.fromisoformat(inp.expense_date)
    if d > date.today():
        raise ValueError("Ngày phát sinh chi phí không được ở tương lai")
    if (date.today() - d).days > 60:
        raise ValueError("Chi phí phát sinh quá 60 ngày, cần xin ngoại lệ với phòng Tài chính")


def _expense_approvers(p: dict, r: Principal) -> list[int]:
    org = r.org
    me = org.employees[r.employee_id]
    if p["amount"] <= EXPENSE_MANAGER_LIMIT and me["manager_id"]:
        return [me["manager_id"]]
    bu_head = org.units[org.bu_of(me["unit_code"])]["head_employee_id"]
    if bu_head and bu_head != r.employee_id:
        return [bu_head]
    conn = hris.connect()
    cfo = [row[0] for row in conn.execute("SELECT employee_id FROM role_assignments WHERE role='cfo'")]
    conn.close()
    return cfo


def _summarize_expense(p: dict, r: Principal) -> str:
    return (f"Đề nghị thanh toán của {r.full_name}: {p['amount']:,} VND ({p['category']}), "
            f"ngày {p['expense_date']}. {p['description']}")


def _execute_expense(p: dict, r: Principal) -> str:
    conn = hris.connect()
    try:
        cur = conn.execute(
            "INSERT INTO expense_claims(employee_id, amount, category, description, expense_date, status, approver_id, created_at) "
            "VALUES (?,?,?,?,?, 'approved', NULL, ?)",
            (r.employee_id, p["amount"], p["category"], p["description"], p["expense_date"], datetime.now().isoformat()))
        conn.commit()
        return f"Đã duyệt đề nghị #{cur.lastrowid}; chuyển kế toán thanh toán trong kỳ chi gần nhất."
    finally:
        conn.close()


register(ToolDef(
    name="submit_expense_claim", input_model=ExpenseInput, requires_approval=True, validate=_validate_expense,
    summarize=_summarize_expense, execute=_execute_expense, approvers=_expense_approvers,
    describe=lambda ctx: (f"Nộp đề nghị thanh toán/hoàn ứng chi phí. ≤ {EXPENSE_MANAGER_LIMIT:,} VND: quản lý trực tiếp duyệt; "
                          "cao hơn: CEO khối duyệt.")))


class ExpenseListInput(ToolInput):
    scope: Literal["self", "team"] = "self"


def _run_expense_list(ctx: ToolContext, inp: ExpenseListInput) -> str:
    p, org = ctx.user, ctx.user.org
    if inp.scope == "self":
        ids = {p.employee_id}
    else:
        ids = policy.scope(p, "expense.individual").employee_ids - {p.employee_id}
        log_access(p, "expense.individual", scope_desc=f"team ({len(ids)})", allowed=bool(ids), audit="standard",
                   conversation_id=ctx.conversation_id)
        if not ids:
            return "Người dùng không có quyền xem đề nghị thanh toán của người khác."
    conn = hris.connect()
    rows = [dict(r) for r in conn.execute(
        f"SELECT id, employee_id, amount, category, description, expense_date, status FROM expense_claims "
        f"WHERE employee_id IN ({','.join('?' * len(ids))}) ORDER BY id DESC LIMIT 50", list(ids))]
    conn.close()
    for r in rows:
        r["employee"] = org.employees[r.pop("employee_id")]["full_name"]
    return json.dumps({"claims": rows, "note": "Đề nghị đang chờ duyệt nằm ở mục Phê duyệt."}, ensure_ascii=False)


register(ToolDef(name="list_expense_claims", input_model=ExpenseListInput, run=_run_expense_list,
                 describe=lambda ctx: "Danh sách đề nghị thanh toán đã duyệt của bản thân (hoặc team nếu có quyền)."))


# --------------------------------------------------------------------------- IT tickets
class TicketInput(ToolInput):
    category: Literal["account", "network_vpn", "email", "hardware", "software", "access_request", "security"]
    title: str
    description: str
    priority: Literal["low", "medium", "high", "critical"]


def _summarize_ticket(p: dict, r: Principal) -> str:
    return f"Ticket [{p['category']}/{p['priority']}] từ {r.full_name}: {p['title']}"


def _execute_ticket(p: dict, r: Principal) -> str:
    conn = hris.connect()
    try:
        cur = conn.execute(
            "INSERT INTO tickets(category, title, description, priority, status, requester_id, created_at) "
            "VALUES (?,?,?,?, 'open', ?, ?)",
            (p["category"], p["title"], p["description"], p["priority"], r.employee_id, datetime.now().isoformat()))
        conn.commit()
        return f"Đã tạo ticket #{cur.lastrowid} (ưu tiên {p['priority']})."
    finally:
        conn.close()


def _ticket_approvers(p: dict, r: Principal) -> list[int]:
    mgr = r.org.employees[r.employee_id]["manager_id"]
    return [mgr] if mgr else []


register(ToolDef(name="create_ticket", input_model=TicketInput, requires_approval=True,
                 summarize=_summarize_ticket, execute=_execute_ticket, approvers=_ticket_approvers,
                 describe=lambda ctx: "Tạo ticket IT (sự cố, yêu cầu phần mềm, cấp quyền truy cập)."))
