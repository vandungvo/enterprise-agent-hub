"""Synthetic data for the FICTIONAL "Sao Mai Group": org chart, personas, employees, payroll, leave, budgets.

Deterministic (random.Random(2026)): every machine and every server instance generates the same data.
Replace this module with HRIS / payroll / ERP connectors in production; nothing else needs to change.
"""
from __future__ import annotations

import random
from datetime import date, timedelta

from app.core.db import engine
from app.hris.org import GROUP_UNIT
from app.hris.payroll import build_payslip, workdays
from app.hris.queries import fetch_value
from app.hris.schema import (
    budgets,
    compensation,
    employees,
    leave_balances,
    leave_requests,
    org_units,
    payslips,
    role_assignments,
)

EMAIL_DOMAIN = "saomai.vn"

ORG = [
    # code, name, type, parent
    (GROUP_UNIT, "Sao Mai Group", "group", None),
    ("SMG", "Sao Mai Games", "bu", GROUP_UNIT),
    ("SMG-STUDIO", "Studio phát triển game", "department", "SMG"),
    ("SMG-ALPHA", "Studio Alpha", "team", "SMG-STUDIO"),
    ("SMG-BETA", "Studio Beta", "team", "SMG-STUDIO"),
    ("SMG-PUB", "Phát hành & Marketing game", "department", "SMG"),
    ("SMP", "Sao Mai Pay", "bu", GROUP_UNIT),
    ("SMP-ENG", "Kỹ thuật thanh toán", "department", "SMP"),
    ("SMP-CORE", "Core Payment", "team", "SMP-ENG"),
    ("SMP-MOBILE", "Mobile App", "team", "SMP-ENG"),
    ("SMP-RISK", "Quản trị rủi ro", "department", "SMP"),
    ("SMC", "Sao Mai Cloud", "bu", GROUP_UNIT),
    ("SMC-ENG", "Cloud Engineering", "department", "SMC"),
    ("SMC-SALES", "Cloud Sales", "department", "SMC"),
    ("PEOPLE", "Khối Con người (HR)", "function", GROUP_UNIT),
    ("FIN", "Khối Tài chính", "function", GROUP_UNIT),
    ("IT", "Khối Công nghệ nội bộ", "function", GROUP_UNIT),
    ("LEGAL", "Pháp chế", "function", GROUP_UNIT),
]
TEAM_SIZES = {"SMG-ALPHA": 9, "SMG-BETA": 7, "SMG-PUB": 8, "SMP-CORE": 8, "SMP-MOBILE": 7, "SMP-RISK": 6,
              "SMC-ENG": 9, "SMC-SALES": 6, "PEOPLE": 5, "FIN": 5, "IT": 5, "LEGAL": 3}
LOCATIONS = ["TP.HCM", "TP.HCM", "TP.HCM", "Hà Nội", "Đà Nẵng"]

# Demo personas with login. scope roles: (role, scope_unit)
PERSONAS = [
    dict(key="ceo", email=f"ceo@{EMAIL_DOMAIN}", full_name="Lê Hoàng Minh", title="Tổng Giám đốc Tập đoàn (Group CEO)",
         level=8, head_of=GROUP_UNIT, roles=[("ceo", GROUP_UNIT), ("exec", GROUP_UNIT)]),
    dict(key="chro", email=f"chro@{EMAIL_DOMAIN}", full_name="Phạm Thu Hà", title="Giám đốc Nhân sự Tập đoàn (CHRO)",
         level=7, head_of="PEOPLE", roles=[("chro", GROUP_UNIT), ("exec", GROUP_UNIT), ("cnb", GROUP_UNIT),
                                           ("auditor", GROUP_UNIT)]),
    dict(key="cfo", email=f"cfo@{EMAIL_DOMAIN}", full_name="Trần Quốc Bảo", title="Giám đốc Tài chính Tập đoàn (CFO)",
         level=7, head_of="FIN", roles=[("cfo", GROUP_UNIT), ("exec", GROUP_UNIT), ("finance", GROUP_UNIT)]),
    dict(key="head_games", email=f"head.games@{EMAIL_DOMAIN}", full_name="Nguyễn Đức Long", title="CEO Sao Mai Games",
         level=7, head_of="SMG", roles=[("exec", "SMG")]),
    dict(key="cnb", email=f"cnb@{EMAIL_DOMAIN}", full_name="Võ Ngọc Lan", title="Chuyên viên C&B",
         level=3, unit="PEOPLE", roles=[("cnb", GROUP_UNIT)]),
    dict(key="hrbp_games", email=f"hrbp.games@{EMAIL_DOMAIN}", full_name="Đặng Mai Anh", title="HR Business Partner - Games",
         level=4, unit="PEOPLE", roles=[("hrbp", "SMG")]),
    dict(key="finance_pay", email=f"finance.pay@{EMAIL_DOMAIN}", full_name="Bùi Thanh Tùng",
         title="Kiểm soát tài chính - Sao Mai Pay", level=4, unit="FIN", roles=[("finance", "SMP")]),
    dict(key="manager_alpha", email=f"manager.alpha@{EMAIL_DOMAIN}", full_name="Hồ Minh Khôi",
         title="Engineering Manager - Studio Alpha", level=5, head_of="SMG-ALPHA", roles=[]),
    dict(key="dev_alpha", email=f"dev.alpha@{EMAIL_DOMAIN}", full_name="Trịnh Gia Huy", title="Senior Game Developer",
         level=3, unit="SMG-ALPHA", roles=[], dependants=1),
    dict(key="itadmin", email=f"itadmin@{EMAIL_DOMAIN}", full_name="Lý Văn Phúc", title="Quản trị hệ thống",
         level=4, unit="IT", roles=[("platform_admin", GROUP_UNIT), ("it_support", GROUP_UNIT)]),
    dict(key="newbie", email=f"newbie@{EMAIL_DOMAIN}", full_name="Châu Ngọc Vy", title="Cloud Engineer (mới gia nhập)",
         level=2, unit="SMC-ENG", roles=[], hired_days_ago=9),
]

LAST = ["Nguyễn", "Trần", "Lê", "Phạm", "Hoàng", "Huỳnh", "Phan", "Vũ", "Võ", "Đặng", "Bùi", "Đỗ", "Hồ", "Ngô", "Dương", "Lý"]
MID_M, MID_F = ["Văn", "Đức", "Minh", "Quốc", "Hữu", "Thành", "Gia"], ["Thị", "Ngọc", "Thu", "Mai", "Thanh", "Bảo", "Kim"]
FIRST_M = ["An", "Bình", "Cường", "Dũng", "Hải", "Hiếu", "Khang", "Lâm", "Nam", "Phong", "Quân", "Sơn", "Tài", "Thắng", "Tuấn", "Việt"]
FIRST_F = ["Anh", "Châu", "Diệp", "Giang", "Hạnh", "Hương", "Linh", "My", "Nhi", "Oanh", "Phương", "Quỳnh", "Trang", "Uyên", "Vân", "Yến"]
TITLES = {
    1: "Nhân viên", 2: "Chuyên viên", 3: "Chuyên viên cao cấp", 4: "Trưởng nhóm / Chuyên gia",
    5: "Quản lý", 6: "Giám đốc khối", 7: "Giám đốc điều hành", 8: "Tổng Giám đốc"}
SALARY_RANGE = {1: (12, 18), 2: (18, 30), 3: (30, 48), 4: (45, 70), 5: (60, 95), 6: (100, 170), 7: (180, 300), 8: (350, 450)}
HEAD_LEVEL = {"group": 8, "bu": 7, "function": 6, "department": 6, "team": 5}


def _strip(s: str) -> str:
    from app.rag.text import strip_accents
    return strip_accents(s).lower().replace(" ", "")


EMPLOYEE_COLUMNS = ("id", "emp_code", "email", "full_name", "gender", "dob", "personal_phone", "national_id",
                    "address", "dependants", "title", "level", "unit_code", "manager_id", "location", "hire_date",
                    "status", "termination_date", "termination_reason", "performance_rating")


def seed_hris() -> None:
    """Generate the synthetic group once (idempotent). Rows are built in memory and bulk-inserted in one
    transaction, so seeding a remote PostgreSQL takes a handful of round trips instead of thousands.
    The RNG call order is fixed: the same data is produced on every machine and every instance."""
    if fetch_value("SELECT COUNT(*) FROM employees"):
        return
    rng = random.Random(2026)
    today = date.today()
    used_emails: set[str] = set()
    next_id = [1]
    rows: dict = {t: [] for t in (employees, compensation, payslips, leave_balances,
                                                      leave_requests, org_units, role_assignments, budgets)}
    emp_rows: dict[int, dict] = {}

    def add_leave(**r) -> None:
        rows[leave_requests].append(r)

    def new_employee(unit: str, level: int, manager_id: int | None, persona: dict | None = None,
                     terminated: bool = False) -> int:
        eid = next_id[0]
        next_id[0] += 1
        gender = rng.choice("MF")
        if persona:
            full_name, email = persona["full_name"], persona["email"]
            title = persona["title"]
        else:
            last = rng.choice(LAST)
            mid = rng.choice(MID_M if gender == "M" else MID_F)
            first = rng.choice(FIRST_M if gender == "M" else FIRST_F)
            full_name = f"{last} {mid} {first}"
            base = _strip(first) + _strip(last)[0] + _strip(mid)[0]
            email, i = f"{base}@{EMAIL_DOMAIN}", 2
            while email in used_emails:
                email, i = f"{base}{i}@{EMAIL_DOMAIN}", i + 1
            title = TITLES[level]
        used_emails.add(email)
        if persona and persona.get("hired_days_ago"):
            hire = today - timedelta(days=persona["hired_days_ago"])
        else:
            hire = today - timedelta(days=rng.randint(200, 365 * (3 + level)))
        term_date = term_reason = None
        status = "active"
        if terminated:
            status = "terminated"
            term_date = (today - timedelta(days=rng.randint(10, 360))).isoformat()
            term_reason = rng.choice(["Nghỉ việc tự nguyện - cơ hội mới", "Nghỉ việc tự nguyện - lý do cá nhân",
                                      "Nghỉ việc tự nguyện - du học", "Hết hạn hợp đồng"])
            if date.fromisoformat(term_date) <= hire:
                hire = date.fromisoformat(term_date) - timedelta(days=rng.randint(200, 900))
        dob = date(today.year - rng.randint(23 + level, 30 + 3 * level), rng.randint(1, 12), rng.randint(1, 28))
        values = (eid, f"SM{eid:04d}", email, full_name, gender, dob.isoformat(), f"09{rng.randint(10_000_000, 99_999_999)}",
                  f"0790{rng.randint(10_000_000, 99_999_999)}", f"{rng.randint(1, 300)} đường số {rng.randint(1, 40)}, {rng.choice(LOCATIONS)}",
                  persona.get("dependants", rng.choice([0, 0, 1, 2])) if persona else rng.choice([0, 0, 1, 2]),
                  title, level, unit, manager_id, rng.choice(LOCATIONS), hire.isoformat(), status, term_date, term_reason,
                  rng.choices("ABCD", weights=[2, 5, 2, 1])[0])
        emp = dict(zip(EMPLOYEE_COLUMNS, values, strict=True))
        rows[employees].append(emp)
        emp_rows[eid] = emp
        # compensation history
        lo, hi = SALARY_RANGE[level]
        current = rng.randint(lo, hi) * 1_000_000
        start_salary = int(current / rng.uniform(1.05, 1.35) / 100_000) * 100_000
        rows[compensation].append(dict(employee_id=eid, effective_date=hire.isoformat(), base_salary=start_salary,
                                       allowance=1_500_000, reason="Lương khởi điểm"))
        if (today - hire).days > 400:
            rows[compensation].append(dict(employee_id=eid, effective_date=date(today.year, 1, 1).isoformat(),
                                           base_salary=current, allowance=2_000_000 + 500_000 * min(level, 6),
                                           reason="Điều chỉnh lương định kỳ"))
        else:
            current = start_salary
        # payslips: last 6 months
        allowance = 2_000_000 + 500_000 * min(level, 6) if (today - hire).days > 400 else 1_500_000
        for back in range(6, 0, -1):
            y, m = today.year, today.month - back
            while m <= 0:
                y, m = y - 1, m + 12
            period_end = date(y, m, 28)
            if period_end < hire or (term_date and date(y, m, 1) > date.fromisoformat(term_date)):
                continue
            overtime = rng.choice([0, 0, 0, 1, 2, 3]) * 800_000 if level <= 3 else 0
            bonus = int(current * rng.uniform(0.3, 1.0) / 100_000) * 100_000 if m in (3, 6, 9, 12) else 0
            slip = build_payslip(current, allowance, overtime, bonus, emp["dependants"])
            rows[payslips].append(dict(employee_id=eid, period=f"{y}-{m:02d}", **slip))
        # leave
        if not terminated:
            seniority = (today - hire).days // (365 * 5)
            entitled = 12 + seniority
            carried = rng.choice([0, 0, 1, 2, 3])
            used = min(entitled, rng.choice([0, 1, 2, 3, 4, 5, 6, 8]))
            sick = rng.choice([0, 0, 1, 2])
            rows[leave_balances].append(dict(employee_id=eid, year=today.year, entitled=entitled,
                                             carried_over=carried, used=used, sick_used=sick))
            remaining, cursor = used, date(today.year, 1, 8)
            while remaining > 0 and cursor < today:
                days = min(remaining, rng.choice([1, 1, 2, 3]))
                start = cursor + timedelta(days=rng.randint(5, 40))
                while start.weekday() >= 5:
                    start += timedelta(days=1)
                end = start
                while workdays(start, end) < days:
                    end += timedelta(days=1)
                if end >= today:
                    break
                add_leave(employee_id=eid, start_date=start.isoformat(), end_date=end.isoformat(), days=days,
                          leave_type="annual", reason="Việc cá nhân", status="approved", approver_id=manager_id,
                          created_at=(start - timedelta(days=7)).isoformat())
                remaining -= days
                cursor = end
        return eid

    # units, heads, members
    unit_head: dict[str, int] = {}
    persona_by_head = {p["head_of"]: p for p in PERSONAS if p.get("head_of")}
    for code, name, typ, parent in ORG:
        mgr = unit_head.get(parent) if parent else None
        persona = persona_by_head.get(code)
        level = persona["level"] if persona else HEAD_LEVEL[typ]
        eid = new_employee(code, level, mgr, persona)
        if not persona:
            emp_rows[eid]["title"] = f"Trưởng đơn vị - {name}"
        unit_head[code] = eid
        rows[org_units].append(dict(code=code, name=name, type=typ, parent_code=parent, head_employee_id=eid))

    persona_ids: dict[str, int] = {p["key"]: unit_head[p["head_of"]] for p in PERSONAS if p.get("head_of")}
    for p in PERSONAS:
        if p.get("unit"):
            persona_ids[p["key"]] = new_employee(p["unit"], p["level"], unit_head[p["unit"]], p)
    for unit, size in TEAM_SIZES.items():
        existing = sum(1 for e in emp_rows.values() if e["unit_code"] == unit and e["id"] != unit_head[unit])
        for _ in range(max(0, size - existing)):
            new_employee(unit, rng.choices([1, 2, 3, 4], weights=[2, 4, 3, 1])[0], unit_head[unit])
        for _ in range(rng.choice([0, 1, 1, 2])):  # leavers during the last 12 months
            new_employee(unit, rng.choice([1, 2, 3]), unit_head[unit], terminated=True)

    for p in PERSONAS:
        for role, scope in p["roles"]:
            rows[role_assignments].append(dict(employee_id=persona_ids[p["key"]], role=role, scope_unit=scope))

    # a few upcoming approved leaves in Studio Alpha (team calendar demo)
    alpha = sorted(e["id"] for e in emp_rows.values() if e["unit_code"] == "SMG-ALPHA" and e["status"] == "active")
    for eid, (offset, days, typ) in zip(alpha[1:4], [(3, 2, "annual"), (6, 1, "sick"), (10, 3, "annual")], strict=False):
        start = today + timedelta(days=offset)
        while start.weekday() >= 5:
            start += timedelta(days=1)
        end = start
        while workdays(start, end) < days:
            end += timedelta(days=1)
        add_leave(employee_id=eid, start_date=start.isoformat(), end_date=end.isoformat(), days=days, leave_type=typ,
                  reason="Khám bệnh" if typ == "sick" else "Việc gia đình", status="approved",
                  approver_id=unit_head["SMG-ALPHA"], created_at=today.isoformat())

    # budgets (VND) for BU / function / department units, Jan .. current month
    for code, _name, typ, _parent in ORG:
        if typ not in ("bu", "function", "department"):
            continue
        scale = {"bu": 3.0, "function": 1.0, "department": 1.4}[typ]
        for m in range(1, today.month + 1):
            for cat, base in [("Nhân sự", 2500), ("Marketing", 900), ("Hạ tầng & cloud", 700), ("Công tác & đào tạo", 120)]:
                planned = int(base * scale * rng.uniform(0.8, 1.2)) * 1_000_000
                actual = int(planned * rng.gauss(1.0, 0.12) / 1_000_000) * 1_000_000 if m < today.month else int(planned * 0.55)
                rows[budgets].append(dict(unit_code=code, period=f"{today.year}-{m:02d}", category=cat,
                                          planned=planned, actual=actual))

    with engine.begin() as conn:
        for table, data in rows.items():
            if data:
                conn.execute(table.insert(), data)
