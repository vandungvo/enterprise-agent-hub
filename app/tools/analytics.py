"""Leadership analytics: workforce & compensation aggregates, budgets.

Population is ALWAYS the intersection of what was asked and what the policy allows. Compensation
aggregates apply k-anonymity (small groups suppressed) plus complementary suppression so a hidden
group cannot be recovered as "total minus the other groups".
"""
from __future__ import annotations

import json
import statistics
from calendar import monthrange
from datetime import date
from typing import Literal

from pydantic import Field

from app import hris
from app.access import AccessDenied, log_access, policy
from app.tools.base import ToolContext, ToolDef, ToolInput, register

COMP_METRICS = {"payroll_cost", "overtime_cost", "avg_base_salary", "median_base_salary"}
Metric = Literal["headcount", "new_hires", "terminations", "attrition_rate", "leave_days_taken",
                 "payroll_cost", "overtime_cost", "avg_base_salary", "median_base_salary"]
GroupBy = Literal["none", "bu", "department", "unit", "level", "location", "month"]


def _dump(o) -> str:
    return json.dumps(o, ensure_ascii=False, default=str)


def _months(start: str, end: str) -> list[str]:
    y, m = map(int, start.split("-"))
    ey, em = map(int, end.split("-"))
    if (y, m) > (ey, em):
        raise ValueError("period_from phải trước period_to")
    out = []
    while (y, m) <= (ey, em):
        out.append(f"{y}-{m:02d}")
        y, m = (y + 1, 1) if m == 12 else (y, m + 1)
    if len(out) > 36:
        raise ValueError("Khoảng thời gian tối đa 36 tháng")
    return out


def _month_end(ym: str) -> date:
    y, m = map(int, ym.split("-"))
    return date(y, m, monthrange(y, m)[1])


def _default_period() -> tuple[str, str]:
    t = date.today()
    y, m = t.year, t.month - 11
    while m <= 0:
        y, m = y - 1, m + 12
    return f"{y}-{m:02d}", f"{t.year}-{t.month:02d}"


def _active(e: dict, d: date) -> bool:
    return e["hire_date"] <= d.isoformat() and (not e["termination_date"] or e["termination_date"] > d.isoformat())


def describe_scope(org: hris.Org, ids: set[int]) -> str:
    if ids >= set(org.employees):
        return "Toàn tập đoàn"
    leaf = {org.employees[i]["unit_code"] for i in ids}
    pick = (lambda u: u) if len(leaf) <= 6 else org.department_of
    units = sorted({org.units[pick(u)]["name"] for u in leaf})
    more = f" và {len(units) - 6} đơn vị khác" if len(units) > 6 else ""
    return f"{len(ids)} nhân sự (gồm cả người đã nghỉ) thuộc: {', '.join(units[:6])}{more}"


def _population(ctx: ToolContext, resource: str, unit_code: str | None, what: str) -> tuple[set[int], str, object]:
    p, org = ctx.user, ctx.user.org
    dec = policy.scope(p, resource)
    if not dec.allowed:
        log_access(p, resource, scope_desc=what, allowed=False, audit="standard", conversation_id=ctx.conversation_id)
        raise AccessDenied("Người dùng không có quyền xem số liệu tổng hợp loại này.")
    pop, note = set(dec.employee_ids), ""
    if unit_code:
        if unit_code not in org.units:
            raise ValueError(f"Không có đơn vị {unit_code}. Các mã hợp lệ: {', '.join(org.units)}")
        unit_ids = org.employees_in_units(org.descendants(unit_code))
        inter = unit_ids & pop
        if not inter:
            log_access(p, resource, scope_desc=f"{what} unit={unit_code}", allowed=False, audit="standard",
                       conversation_id=ctx.conversation_id)
            raise AccessDenied(f"Đơn vị {org.units[unit_code]['name']} nằm ngoài phạm vi quyền của người dùng.")
        if inter != unit_ids:
            note = "Chỉ tính phần của đơn vị nằm trong phạm vi quyền của người dùng."
        pop = inter
    log_access(p, resource, scope_desc=f"{what} unit={unit_code or '-'} n={len(pop)}", allowed=True,
               audit=dec.audit, conversation_id=ctx.conversation_id)
    return pop, note, dec


# --------------------------------------------------------------------------- workforce_analytics
class WorkforceInput(ToolInput):
    metric: Metric
    group_by: GroupBy = "none"
    unit_code: str | None = Field(default=None, description="Lọc theo đơn vị (gồm đơn vị con)")
    period_from: str | None = Field(default=None, description="YYYY-MM (mặc định: 12 tháng gần nhất)")
    period_to: str | None = Field(default=None, description="YYYY-MM (mặc định: tháng hiện tại)")


def _run_workforce(ctx: ToolContext, inp: WorkforceInput) -> str:
    org = ctx.user.org
    comp = inp.metric in COMP_METRICS
    resource = "compensation.aggregate" if comp else "workforce.aggregate"
    pop, note, dec = _population(ctx, resource, inp.unit_code, f"{inp.metric} by {inp.group_by}")
    d_from, d_to = _default_period()
    months = _months(inp.period_from or d_from, inp.period_to or d_to)
    start, end = date.fromisoformat(months[0] + "-01"), _month_end(months[-1])
    emps = {i: org.employees[i] for i in pop}
    if inp.group_by == "month" and inp.metric in {"avg_base_salary", "median_base_salary"}:
        raise ValueError("Lương trung bình/trung vị không hỗ trợ group_by=month; dùng payroll_cost cho xu hướng.")

    def key(e: dict) -> str:
        g = inp.group_by
        if g == "bu":
            return org.units[org.bu_of(e["unit_code"])]["name"]
        if g == "department":
            return org.units[org.department_of(e["unit_code"])]["name"]
        if g == "unit":
            return org.units[e["unit_code"]]["name"]
        if g == "level":
            return f"L{e['level']}"
        if g == "location":
            return e["location"]
        return "Tổng"

    groups: dict[str, dict] = {}

    def add(k: str, value: float, emp_id: int):
        g = groups.setdefault(k, {"value": 0.0, "ids": set(), "values": []})
        g["value"] += value
        g["ids"].add(emp_id)
        g["values"].append(value)

    by_month = inp.group_by == "month"
    m = inp.metric
    if m == "headcount":
        if by_month:
            for ym in months:
                for e in emps.values():
                    if _active(e, _month_end(ym)):
                        add(ym, 1, e["id"])
        else:
            for e in emps.values():
                if _active(e, end):
                    add(key(e), 1, e["id"])
    elif m in ("new_hires", "terminations"):
        field = "hire_date" if m == "new_hires" else "termination_date"
        for e in emps.values():
            v = e[field]
            if v and start.isoformat() <= v <= end.isoformat():
                add(v[:7] if by_month else key(e), 1, e["id"])
    elif m == "attrition_rate":
        buckets: dict[str, dict] = {}
        for e in emps.values():
            ks = months if by_month else [key(e)]
            for k in ks:
                b = buckets.setdefault(k, {"terms": 0, "hc_start": 0, "hc_end": 0, "ids": set()})
                s, t = (date.fromisoformat(k + "-01"), _month_end(k)) if by_month else (start, end)
                b["hc_start"] += _active(e, s)
                b["hc_end"] += _active(e, t)
                if e["termination_date"] and s.isoformat() <= e["termination_date"] <= t.isoformat():
                    b["terms"] += 1
                if _active(e, t) or b["terms"]:
                    b["ids"].add(e["id"])
        for k, b in buckets.items():
            avg_hc = (b["hc_start"] + b["hc_end"]) / 2
            groups[k] = {"value": round(100 * b["terms"] / avg_hc, 1) if avg_hc else 0.0, "ids": b["ids"],
                         "extra": {"terminations": b["terms"], "avg_headcount": avg_hc}}
    else:
        if m == "leave_days_taken":
            rows = hris.fetch_all("SELECT employee_id, start_date, days FROM leave_requests WHERE status = 'approved' "
                                  "AND start_date BETWEEN :start AND :end AND employee_id IN :ids",
                                  start=start.isoformat(), end=end.isoformat(), ids=pop)
            for r in rows:
                add(r["start_date"][:7] if by_month else key(emps[r["employee_id"]]), r["days"], r["employee_id"])
        elif m in ("payroll_cost", "overtime_cost"):
            col = "gross" if m == "payroll_cost" else "overtime"  # fixed whitelist, not user input
            rows = hris.fetch_all(f"SELECT employee_id, period, {col} AS v FROM payslips "
                                  "WHERE period BETWEEN :p_from AND :p_to AND employee_id IN :ids",
                                  p_from=months[0], p_to=months[-1], ids=pop)
            for r in rows:
                add(r["period"] if by_month else key(emps[r["employee_id"]]), r["v"], r["employee_id"])
        else:  # avg / median base salary of people active at period end
            rows = hris.fetch_all("SELECT employee_id, base_salary, effective_date FROM compensation "
                                  "WHERE effective_date <= :end AND employee_id IN :ids ORDER BY effective_date, id",
                                  end=end.isoformat(), ids=pop)
            latest = {r["employee_id"]: r["base_salary"] for r in rows}
            for eid, base in latest.items():
                if _active(emps[eid], end):
                    add(key(emps[eid]), base, eid)
            for g in groups.values():
                vals = g["values"]
                g["value"] = statistics.mean(vals) if m == "avg_base_salary" else statistics.median(vals)

    # ---- k-anonymity for compensation aggregates
    k = dec.min_group_size if comp else 1
    rows_out, suppressed = [], []
    for name, g in sorted(groups.items()):
        n = len(g["ids"])
        hide = n < k
        rows_out.append({"group": name, "value": None if hide else round(g["value"]), "employees": n,
                         "suppressed": hide, **g.get("extra", {})})
        if hide:
            suppressed.append(name)
    if comp and len(suppressed) == 1 and len(rows_out) > 1:
        visible = [r for r in rows_out if not r["suppressed"]]
        if visible:
            smallest = min(visible, key=lambda r: r["employees"])
            smallest.update(value=None, suppressed=True)
            suppressed.append(smallest["group"] + " (ẩn bổ sung để không suy ra nhóm bị ẩn)")
    if m == "attrition_rate":
        for r in rows_out:
            r["value"] = groups[r["group"]]["value"]
    total_ids = set().union(*(g["ids"] for g in groups.values())) if groups else set()
    total = None
    if m in ("headcount", "new_hires", "terminations", "leave_days_taken", "payroll_cost", "overtime_cost") \
            and len(total_ids) >= k and not by_month:
        total = round(sum(g["value"] for g in groups.values()))
    return _dump({
        "metric": m, "unit": "VND" if comp else ("%" if m == "attrition_rate" else ("ngày" if m == "leave_days_taken" else "người")),
        "period": f"{months[0]} → {months[-1]}", "scope": describe_scope(org, pop), "scope_note": note or None,
        "group_by": inp.group_by, "total": total, "rows": rows_out,
        "privacy": {"min_group_size": k, "suppressed_groups": suppressed} if comp else None,
    })


register(ToolDef(
    name="workforce_analytics", input_model=WorkforceInput, run=_run_workforce,
    describe=lambda ctx: (
        "Số liệu nhân sự tổng hợp: headcount, new_hires, terminations, attrition_rate (%), leave_days_taken, "
        "payroll_cost (tổng gross), overtime_cost, avg_base_salary, median_base_salary. Hệ thống tự giới hạn "
        "theo phạm vi quyền; nhóm quá nhỏ bị ẩn với số liệu lương. Mã đơn vị: "
        + ", ".join(f"{c} ({u['name']})" for c, u in ctx.user.org.units.items()))))


# --------------------------------------------------------------------------- budget_report
class BudgetInput(ToolInput):
    unit_code: str | None = Field(default=None, description="Mã đơn vị (bỏ trống = các đơn vị cao nhất trong phạm vi quyền)")
    period_from: str | None = Field(default=None, description="YYYY-MM (mặc định: đầu năm)")
    period_to: str | None = Field(default=None, description="YYYY-MM (mặc định: tháng hiện tại)")
    group_by: Literal["unit", "category", "month"] = "category"


def _run_budget(ctx: ToolContext, inp: BudgetInput) -> str:
    p, org = ctx.user, ctx.user.org
    allowed = policy.unit_scope(p, "finance.budget")
    if not allowed:
        log_access(p, "finance.budget", scope_desc="budget", allowed=False, audit="standard", conversation_id=ctx.conversation_id)
        raise AccessDenied("Người dùng không có quyền xem ngân sách. Ngân sách chỉ dành cho trưởng đơn vị, tài chính và lãnh đạo.")
    if inp.unit_code:
        if inp.unit_code not in org.units:
            raise ValueError(f"Không có đơn vị {inp.unit_code}")
        if inp.unit_code not in allowed:
            log_access(p, "finance.budget", scope_desc=f"unit={inp.unit_code}", allowed=False, audit="standard",
                       conversation_id=ctx.conversation_id)
            raise AccessDenied(f"Ngân sách của {org.units[inp.unit_code]['name']} nằm ngoài phạm vi quyền.")
        roots = [inp.unit_code]
    else:
        roots = sorted(u for u in allowed if org.units[u]["parent_code"] not in allowed)
    t = date.today()
    months = _months(inp.period_from or f"{t.year}-01", inp.period_to or f"{t.year}-{t.month:02d}")
    log_access(p, "finance.budget", scope_desc=f"roots={roots}", allowed=True, audit="standard", conversation_id=ctx.conversation_id)
    result = []
    for root in roots:
        units = org.descendants(root) & allowed
        rows = hris.fetch_all("SELECT unit_code, period, category, planned, actual FROM budgets "
                              "WHERE period BETWEEN :p_from AND :p_to AND unit_code IN :units",
                              p_from=months[0], p_to=months[-1], units=units)
        agg: dict[str, list[int]] = {}
        for r in rows:
            if inp.group_by == "category":
                k = r["category"]
            elif inp.group_by == "month":
                k = r["period"]
            else:  # roll up to direct children of root
                path = org.ancestors(r["unit_code"])
                idx = path.index(root)
                k = org.units[path[idx + 1] if len(path) > idx + 1 else root]["name"]
            a = agg.setdefault(k, [0, 0])
            a[0] += r["planned"]
            a[1] += r["actual"]
        lines = [{"group": k, "planned": v[0], "actual": v[1],
                  "variance_pct": round(100 * (v[1] - v[0]) / v[0], 1) if v[0] else None} for k, v in sorted(agg.items())]
        tp, ta = sum(v[0] for v in agg.values()), sum(v[1] for v in agg.values())
        result.append({"unit": org.units[root]["name"], "unit_code": root, "planned_total": tp, "actual_total": ta,
                       "variance_pct": round(100 * (ta - tp) / tp, 1) if tp else None, "lines": lines})
    return _dump({"currency": "VND", "period": f"{months[0]} → {months[-1]}",
                  "note": "Tháng hiện tại là số thực tế tạm tính (chưa khoá sổ).", "reports": result})


register(ToolDef(name="budget_report", input_model=BudgetInput, run=_run_budget,
                 describe=lambda ctx: "Báo cáo ngân sách kế hoạch vs thực tế theo đơn vị (cộng dồn đơn vị con), theo hạng mục / tháng / đơn vị con. Giới hạn theo phạm vi quyền."))
