"""People tools: directory, org chart, profile, payroll, leave. Every read goes through the policy engine."""
from __future__ import annotations

import json
from datetime import date, datetime
from typing import Literal

from pydantic import Field

from .. import hris
from ..policy import AccessDenied, Principal, log_access, policy
from ..rag.text import strip_accents
from .base import ToolContext, ToolDef, ToolInput, register

EMP_REF = ("Email, mã nhân viên (SMxxxx) hoặc họ tên của người cần tra cứu. "
           "BỎ TRỐNG để lấy dữ liệu của chính người dùng.")
PUBLIC_FIELDS = ("emp_code", "full_name", "title", "unit", "email", "manager", "location")


def _dump(obj) -> str:
    return json.dumps(obj, ensure_ascii=False, default=str)


def resolve_target(ctx: ToolContext, ref: str | None) -> int:
    if not ref or ref.strip().lower() in {"me", "tôi", "toi", "self", ctx.user.email}:
        return ctx.user.employee_id
    emp_id = ctx.user.org.resolve(ref)
    if emp_id is None:
        raise ValueError(f"Không xác định được duy nhất nhân viên '{ref}'. Dùng directory_search để tìm email/mã nhân viên.")
    return emp_id


def public_card(org: hris.Org, emp_id: int) -> dict:
    e = org.employees[emp_id]
    mgr = org.employees.get(e["manager_id"]) if e["manager_id"] else None
    return {"emp_code": e["emp_code"], "full_name": e["full_name"], "title": e["title"],
            "unit": org.units[e["unit_code"]]["name"], "unit_code": e["unit_code"], "email": e["email"],
            "manager": f"{mgr['full_name']} ({mgr['email']})" if mgr else None, "location": e["location"],
            "status": "đang làm việc" if e["status"] == "active" else "đã nghỉ việc"}


# --------------------------------------------------------------------------- directory_search
class DirectoryInput(ToolInput):
    query: str = Field(description="Tên, chức danh, email hoặc tên đơn vị (không dấu cũng được)")
    unit_code: str | None = Field(default=None, description="Giới hạn trong đơn vị (gồm đơn vị con)")


def _run_directory(ctx: ToolContext, inp: DirectoryInput) -> str:
    org = ctx.user.org
    allowed = policy.scope(ctx.user, "directory.public").employee_ids
    units = org.descendants(inp.unit_code) if inp.unit_code and inp.unit_code in org.units else None
    terms = strip_accents(inp.query).lower().split()
    hits = []
    for e in org.employees.values():
        if e["status"] != "active" or e["id"] not in allowed or (units and e["unit_code"] not in units):
            continue
        hay = strip_accents(f"{e['full_name']} {e['title']} {e['email']} {org.units[e['unit_code']]['name']} "
                            f"{e['unit_code']} {e['emp_code']}").lower()
        if all(t in hay for t in terms):
            hits.append(public_card(org, e["id"]))
    return _dump({"count": len(hits), "results": hits[:15], "truncated": len(hits) > 15})


register(ToolDef(name="directory_search", input_model=DirectoryInput, run=_run_directory,
                 describe=lambda ctx: "Danh bạ nội bộ: tìm đồng nghiệp theo tên/chức danh/đơn vị. Chỉ trả thông tin công việc công khai nội bộ."))


# --------------------------------------------------------------------------- get_org_chart
class OrgChartInput(ToolInput):
    unit_code: str | None = Field(default=None, description="Mã đơn vị (bỏ trống = cấp tập đoàn)")


def _run_org_chart(ctx: ToolContext, inp: OrgChartInput) -> str:
    org = ctx.user.org
    code = inp.unit_code or hris.GROUP_UNIT
    if code not in org.units:
        return _dump({"error": f"Không có đơn vị {code}", "units": {c: u["name"] for c, u in org.units.items()}})

    def node(c: str) -> dict:
        u = org.units[c]
        head = org.employees.get(u["head_employee_id"])
        return {"code": c, "name": u["name"], "type": u["type"],
                "head": f"{head['full_name']} - {head['title']}" if head else None,
                "active_headcount": sum(1 for e in org.employees.values()
                                        if e["status"] == "active" and e["unit_code"] in org.descendants(c))}

    return _dump({"path": [org.units[a]["name"] for a in org.ancestors(code)], "unit": node(code),
                  "children": [node(c) for c in org.children.get(code, [])]})


register(ToolDef(name="get_org_chart", input_model=OrgChartInput, run=_run_org_chart,
                 describe=lambda ctx: "Sơ đồ tổ chức: đơn vị, trưởng đơn vị, đơn vị con và quân số. Mã đơn vị gốc: " + hris.GROUP_UNIT))


# --------------------------------------------------------------------------- get_employee_profile
class EmployeeRefInput(ToolInput):
    employee: str | None = Field(default=None, description=EMP_REF)


def _run_profile(ctx: ToolContext, inp: EmployeeRefInput) -> str:
    target = resolve_target(ctx, inp.employee)
    p, org = ctx.user, ctx.user.org
    out = {"public": public_card(org, target), "hidden_sections": []}
    conn = hris.connect()
    row = dict(conn.execute("SELECT * FROM employees WHERE id=?", (target,)).fetchone())
    conn.close()
    for resource, fields, key in [
        ("profile.employment", ("level", "hire_date", "status", "termination_date", "termination_reason"), "employment"),
        ("profile.personal", ("gender", "dob", "personal_phone", "national_id", "address", "dependants",
                              "performance_rating"), "personal"),
    ]:
        d = policy.check(p, resource, target)
        log_access(p, resource, target_id=target, allowed=d.allowed, audit=d.audit,
                   conversation_id=ctx.conversation_id, sink=ctx.sensitive)
        if d.allowed:
            out[key] = {f: row[f] for f in fields}
        else:
            out["hidden_sections"].append(f"{key} (không có quyền)")
    return _dump(out)


register(ToolDef(name="get_employee_profile", input_model=EmployeeRefInput, run=_run_profile,
                 describe=lambda ctx: "Hồ sơ nhân viên. Các phần không có quyền xem sẽ được ẩn tự động."))


# --------------------------------------------------------------------------- payroll
class PayslipInput(ToolInput):
    period: str | None = Field(default=None, description="Kỳ lương YYYY-MM (bỏ trống = kỳ gần nhất)")
    employee: str | None = Field(default=None, description=EMP_REF)


def _run_payslip(ctx: ToolContext, inp: PayslipInput) -> str:
    target = resolve_target(ctx, inp.employee)
    policy.require(ctx.user, "compensation.individual", target, conversation_id=ctx.conversation_id, sink=ctx.sensitive)
    conn = hris.connect()
    periods = [r[0] for r in conn.execute("SELECT period FROM payslips WHERE employee_id=? ORDER BY period DESC", (target,))]
    if not periods:
        conn.close()
        return "Chưa có phiếu lương nào."
    period = inp.period or periods[0]
    row = conn.execute("SELECT * FROM payslips WHERE employee_id=? AND period=?", (target, period)).fetchone()
    deps = conn.execute("SELECT dependants FROM employees WHERE id=?", (target,)).fetchone()[0]
    conn.close()
    if row is None:
        return _dump({"error": f"Không có phiếu lương kỳ {period}", "available_periods": periods})
    slip = dict(row)
    slip.pop("employee_id")
    return _dump({"employee": ctx.user.org.employees[target]["full_name"], "currency": "VND", "payslip": slip,
                  "deductions_applied": {"personal": hris.PERSONAL_DEDUCTION, "dependants": deps,
                                         "per_dependant": hris.DEPENDANT_DEDUCTION},
                  "available_periods": periods})


register(ToolDef(name="get_payslip", input_model=PayslipInput, run=_run_payslip,
                 describe=lambda ctx: "Phiếu lương chi tiết theo kỳ (gross, bảo hiểm, thuế TNCN, thực nhận). Dữ liệu tuyệt mật, hệ thống tự kiểm tra quyền."))


def _run_comp_history(ctx: ToolContext, inp: EmployeeRefInput) -> str:
    target = resolve_target(ctx, inp.employee)
    policy.require(ctx.user, "compensation.individual", target, conversation_id=ctx.conversation_id, sink=ctx.sensitive)
    conn = hris.connect()
    rows = [dict(r) for r in conn.execute(
        "SELECT effective_date, base_salary, allowance, reason FROM compensation WHERE employee_id=? ORDER BY effective_date",
        (target,))]
    conn.close()
    return _dump({"employee": ctx.user.org.employees[target]["full_name"], "currency": "VND", "history": rows})


register(ToolDef(name="get_compensation_history", input_model=EmployeeRefInput, run=_run_comp_history,
                 describe=lambda ctx: "Lịch sử lương cơ bản / phụ cấp và các lần điều chỉnh."))


# --------------------------------------------------------------------------- leave
def _run_leave_balance(ctx: ToolContext, inp: EmployeeRefInput) -> str:
    target = resolve_target(ctx, inp.employee)
    policy.require(ctx.user, "leave.individual", target, conversation_id=ctx.conversation_id, sink=ctx.sensitive)
    conn = hris.connect()
    bal = conn.execute("SELECT * FROM leave_balances WHERE employee_id=? AND year=?", (target, date.today().year)).fetchone()
    conn.close()
    if bal is None:
        return "Chưa có dữ liệu phép năm nay."
    b = dict(bal)
    return _dump({"employee": ctx.user.org.employees[target]["full_name"], "year": b["year"],
                  "annual_entitled": b["entitled"], "carried_over": b["carried_over"], "annual_used": b["used"],
                  "annual_remaining": b["entitled"] + b["carried_over"] - b["used"], "sick_days_used": b["sick_used"]})


register(ToolDef(name="get_leave_balance", input_model=EmployeeRefInput, run=_run_leave_balance,
                 describe=lambda ctx: "Số ngày phép năm được hưởng, chuyển sang, đã dùng, còn lại, ngày nghỉ ốm."))


class LeaveListInput(ToolInput):
    scope: Literal["self", "team"] = Field(default="self", description="team = toàn bộ tuyến báo cáo (chỉ dành cho quản lý)")
    status: Literal["approved", "pending", "rejected", "all"] = "all"
    year: int | None = None


def _run_leave_list(ctx: ToolContext, inp: LeaveListInput) -> str:
    p, org = ctx.user, ctx.user.org
    if inp.scope == "self":
        ids = {p.employee_id}
    else:
        d = policy.scope(p, "leave.individual")
        ids = d.employee_ids - {p.employee_id}
        if not ids:
            raise AccessDenied("Người dùng không quản lý ai nên không xem được đơn nghỉ của team.")
        log_access(p, "leave.individual", scope_desc=f"team ({len(ids)} người)", allowed=True, audit="standard",
                   conversation_id=ctx.conversation_id)
    year = inp.year or date.today().year
    conn = hris.connect()
    q = (f"SELECT employee_id, start_date, end_date, days, leave_type, status FROM leave_requests "
         f"WHERE employee_id IN ({','.join('?' * len(ids))}) AND substr(start_date,1,4)=?")
    args = [*ids, str(year)]
    if inp.status != "all":
        q += " AND status=?"
        args.append(inp.status)
    rows = [dict(r) | {"employee": org.employees[r["employee_id"]]["full_name"]}
            for r in conn.execute(q + " ORDER BY start_date DESC LIMIT 60", args)]
    conn.close()
    for r in rows:
        r.pop("employee_id")
    return _dump({"year": year, "count": len(rows), "requests": rows})


register(ToolDef(name="list_leave_requests", input_model=LeaveListInput, run=_run_leave_list,
                 describe=lambda ctx: "Danh sách đơn nghỉ của bản thân, hoặc của team (nếu là quản lý). Đơn đang chờ duyệt trên hệ thống phê duyệt không nằm ở đây."))


class CalendarInput(ToolInput):
    start_date: str = Field(description="YYYY-MM-DD")
    end_date: str = Field(description="YYYY-MM-DD")


def _run_calendar(ctx: ToolContext, inp: CalendarInput) -> str:
    p, org = ctx.user, ctx.user.org
    start, end = date.fromisoformat(inp.start_date), date.fromisoformat(inp.end_date)
    if (end - start).days > 62:
        raise ValueError("Khoảng thời gian tối đa 62 ngày")
    ids = policy.scope(p, "leave.calendar").employee_ids
    conn = hris.connect()
    rows = conn.execute(
        f"SELECT employee_id, start_date, end_date, days, leave_type FROM leave_requests WHERE status='approved' "
        f"AND start_date<=? AND end_date>=? AND employee_id IN ({','.join('?' * len(ids))}) ORDER BY start_date",
        [end.isoformat(), start.isoformat(), *ids]).fetchall()
    conn.close()
    out = []
    for r in rows:
        item = {"employee": org.employees[r["employee_id"]]["full_name"], "from": r["start_date"],
                "to": r["end_date"], "days": r["days"]}
        # leave type (e.g. sick = health data) only for people whose leave details the user may see
        item["type"] = r["leave_type"] if policy.check(p, "leave.individual", r["employee_id"]).allowed else "vắng mặt"
        out.append(item)
    return _dump({"from": inp.start_date, "to": inp.end_date, "absences": out,
                  "scope": "tuyến báo cáo của bạn" if "manager" in p.roles else "đồng nghiệp cùng team"})


register(ToolDef(name="team_calendar", input_model=CalendarInput, run=_run_calendar,
                 describe=lambda ctx: "Lịch vắng mặt của đồng nghiệp cùng team (quản lý: cả tuyến báo cáo). Nhân viên chỉ thấy ngày vắng, không thấy loại nghỉ."))


class LeaveInput(ToolInput):
    start_date: str = Field(description="YYYY-MM-DD")
    end_date: str = Field(description="YYYY-MM-DD (bao gồm)")
    leave_type: Literal["annual", "sick", "unpaid", "wedding", "bereavement", "other"]
    reason: str


def _validate_leave(ctx: ToolContext, inp: LeaveInput) -> None:
    try:
        s, e = date.fromisoformat(inp.start_date), date.fromisoformat(inp.end_date)
    except ValueError as exc:
        raise ValueError("Ngày phải theo định dạng YYYY-MM-DD") from exc
    if e < s:
        raise ValueError("Ngày kết thúc phải sau ngày bắt đầu")
    days = hris.workdays(s, e)
    if days == 0:
        raise ValueError("Khoảng thời gian không có ngày làm việc nào")
    if inp.leave_type == "annual":
        conn = hris.connect()
        b = conn.execute("SELECT entitled + carried_over - used FROM leave_balances WHERE employee_id=? AND year=?",
                         (ctx.user.employee_id, s.year)).fetchone()
        conn.close()
        if b is not None and b[0] < days:
            raise ValueError(f"Không đủ phép năm: cần {days} ngày, còn {b[0]} ngày")


def _leave_approvers(payload: dict, r: Principal) -> list[int]:
    mgr = r.org.employees[r.employee_id]["manager_id"]
    if mgr:
        return [mgr]
    conn = hris.connect()
    chro = [row[0] for row in conn.execute("SELECT employee_id FROM role_assignments WHERE role='chro'")]
    conn.close()
    return chro


def _summarize_leave(p: dict, r: Principal) -> str:
    days = hris.workdays(date.fromisoformat(p["start_date"]), date.fromisoformat(p["end_date"]))
    return (f"Đơn nghỉ ({p['leave_type']}) của {r.full_name}: {p['start_date']} → {p['end_date']} "
            f"({days} ngày làm việc). Lý do: {p['reason']}")


def _execute_leave(p: dict, r: Principal) -> str:
    s, e = date.fromisoformat(p["start_date"]), date.fromisoformat(p["end_date"])
    days = hris.workdays(s, e)
    conn = hris.connect()
    try:
        cur = conn.execute(
            "INSERT INTO leave_requests(employee_id, start_date, end_date, days, leave_type, reason, status, approver_id, created_at) "
            "VALUES (?,?,?,?,?,?, 'approved', ?, ?)",
            (r.employee_id, p["start_date"], p["end_date"], days, p["leave_type"], p["reason"],
             r.org.employees[r.employee_id]["manager_id"], datetime.now().isoformat()))
        col = {"annual": "used", "sick": "sick_used"}.get(p["leave_type"])
        if col:
            conn.execute(f"UPDATE leave_balances SET {col} = {col} + ? WHERE employee_id=? AND year=?",
                         (days, r.employee_id, s.year))
        conn.commit()
        return f"Đã ghi nhận đơn nghỉ #{cur.lastrowid} ({days} ngày) vào HRIS."
    finally:
        conn.close()


register(ToolDef(name="submit_leave_request", input_model=LeaveInput, requires_approval=True,
                 describe=lambda ctx: "Nộp đơn nghỉ cho chính người dùng. Đơn chuyển tới quản lý trực tiếp phê duyệt.",
                 validate=_validate_leave, summarize=_summarize_leave, execute=_execute_leave,
                 approvers=_leave_approvers))
