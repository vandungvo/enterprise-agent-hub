"""Demo enterprise systems of record: HRIS (org, employees), payroll, time & leave, finance.

Everything here is synthetic data for a FICTIONAL group ("Sao Mai Group") shaped like a large
Vietnamese tech conglomerate (several business units + corporate functions). In production this
module is replaced by connectors to the real HRIS / payroll / ERP (read through service accounts),
while app/policy.py and the tools keep enforcing access exactly the same way.
"""
from __future__ import annotations

import random
import sqlite3
from datetime import date, timedelta

from .settings import settings

GROUP_UNIT = "SMG-GROUP"
EMAIL_DOMAIN = "saomai.vn"

SCHEMA = """
CREATE TABLE IF NOT EXISTS org_units (
  code TEXT PRIMARY KEY, name TEXT, type TEXT, parent_code TEXT, head_employee_id INTEGER);
CREATE TABLE IF NOT EXISTS employees (
  id INTEGER PRIMARY KEY, emp_code TEXT UNIQUE, email TEXT UNIQUE, full_name TEXT, gender TEXT,
  dob TEXT, personal_phone TEXT, national_id TEXT, address TEXT, dependants INTEGER,
  title TEXT, level INTEGER, unit_code TEXT, manager_id INTEGER, location TEXT,
  hire_date TEXT, status TEXT, termination_date TEXT, termination_reason TEXT,
  performance_rating TEXT);
CREATE TABLE IF NOT EXISTS role_assignments (
  employee_id INTEGER, role TEXT, scope_unit TEXT, PRIMARY KEY (employee_id, role, scope_unit));
CREATE TABLE IF NOT EXISTS compensation (
  employee_id INTEGER, effective_date TEXT, base_salary INTEGER, allowance INTEGER, reason TEXT);
CREATE TABLE IF NOT EXISTS payslips (
  employee_id INTEGER, period TEXT, base INTEGER, allowance INTEGER, overtime INTEGER, bonus INTEGER,
  gross INTEGER, social_insurance INTEGER, health_insurance INTEGER, unemployment_insurance INTEGER,
  pit INTEGER, net INTEGER, PRIMARY KEY (employee_id, period));
CREATE TABLE IF NOT EXISTS leave_balances (
  employee_id INTEGER, year INTEGER, entitled REAL, carried_over REAL, used REAL, sick_used REAL,
  PRIMARY KEY (employee_id, year));
CREATE TABLE IF NOT EXISTS leave_requests (
  id INTEGER PRIMARY KEY, employee_id INTEGER, start_date TEXT, end_date TEXT, days REAL,
  leave_type TEXT, reason TEXT, status TEXT, approver_id INTEGER, created_at TEXT);
CREATE TABLE IF NOT EXISTS budgets (
  unit_code TEXT, period TEXT, category TEXT, planned INTEGER, actual INTEGER,
  PRIMARY KEY (unit_code, period, category));
CREATE TABLE IF NOT EXISTS expense_claims (
  id INTEGER PRIMARY KEY, employee_id INTEGER, amount INTEGER, category TEXT, description TEXT,
  expense_date TEXT, status TEXT, approver_id INTEGER, created_at TEXT);
CREATE TABLE IF NOT EXISTS tickets (
  id INTEGER PRIMARY KEY, category TEXT, title TEXT, description TEXT, priority TEXT, status TEXT,
  requester_id INTEGER, created_at TEXT);
"""

# --------------------------------------------------------------------------- payroll rules (demo)
# Giả định cho dữ liệu mẫu. Khi triển khai thật, C&B cấu hình theo quy định hiện hành.
INSURANCE_CAP = 46_800_000
SI_RATE, HI_RATE, UI_RATE = 0.08, 0.015, 0.01
PERSONAL_DEDUCTION, DEPENDANT_DEDUCTION = 15_500_000, 6_200_000
PIT_BRACKETS = [(5e6, .05), (10e6, .10), (18e6, .15), (32e6, .20), (52e6, .25), (80e6, .30), (float("inf"), .35)]


def compute_pit(taxable: float) -> int:
    tax, lower = 0.0, 0.0
    for upper, rate in PIT_BRACKETS:
        if taxable <= lower:
            break
        tax += (min(taxable, upper) - lower) * rate
        lower = upper
    return int(round(tax, -3))


def build_payslip(base: int, allowance: int, overtime: int, bonus: int, dependants: int) -> dict:
    gross = base + allowance + overtime + bonus
    ins_base = min(base, INSURANCE_CAP)
    si, hi, ui = int(ins_base * SI_RATE), int(ins_base * HI_RATE), int(ins_base * UI_RATE)
    taxable = max(0, gross - si - hi - ui - PERSONAL_DEDUCTION - dependants * DEPENDANT_DEDUCTION)
    pit = compute_pit(taxable)
    return {"base": base, "allowance": allowance, "overtime": overtime, "bonus": bonus, "gross": gross,
            "social_insurance": si, "health_insurance": hi, "unemployment_insurance": ui, "pit": pit,
            "net": gross - si - hi - ui - pit}


def workdays(start: date, end: date) -> int:
    n, d = 0, start
    while d <= end:
        n += d.weekday() < 5
        d += timedelta(days=1)
    return n


def connect() -> sqlite3.Connection:
    conn = sqlite3.connect(settings.business_db_path)
    conn.row_factory = sqlite3.Row
    return conn


# --------------------------------------------------------------------------- org definition
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
    from .rag.text import strip_accents
    return strip_accents(s).lower().replace(" ", "")


def seed_hris() -> None:
    conn = connect()
    conn.executescript(SCHEMA)
    if conn.execute("SELECT COUNT(*) FROM employees").fetchone()[0]:
        conn.close()
        return
    rng = random.Random(2026)
    today = date.today()
    used_emails: set[str] = set()
    next_id = [1]

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
        conn.execute(
            "INSERT INTO employees VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (eid, f"SM{eid:04d}", email, full_name, gender, dob.isoformat(), f"09{rng.randint(10_000_000, 99_999_999)}",
             f"0790{rng.randint(10_000_000, 99_999_999)}", f"{rng.randint(1, 300)} đường số {rng.randint(1, 40)}, {rng.choice(LOCATIONS)}",
             persona.get("dependants", rng.choice([0, 0, 1, 2])) if persona else rng.choice([0, 0, 1, 2]),
             title, level, unit, manager_id, rng.choice(LOCATIONS), hire.isoformat(), status, term_date, term_reason,
             rng.choices("ABCD", weights=[2, 5, 2, 1])[0]))
        # compensation history
        lo, hi = SALARY_RANGE[level]
        current = rng.randint(lo, hi) * 1_000_000
        start_salary = int(current / rng.uniform(1.05, 1.35) / 100_000) * 100_000
        conn.execute("INSERT INTO compensation VALUES (?,?,?,?,?)",
                     (eid, hire.isoformat(), start_salary, 1_500_000, "Lương khởi điểm"))
        if (today - hire).days > 400:
            conn.execute("INSERT INTO compensation VALUES (?,?,?,?,?)",
                         (eid, date(today.year, 1, 1).isoformat(), current, 2_000_000 + 500_000 * min(level, 6),
                          "Điều chỉnh lương định kỳ"))
        else:
            current = start_salary
        # payslips: last 6 months
        allowance = 2_000_000 + 500_000 * min(level, 6) if (today - hire).days > 400 else 1_500_000
        dependants = conn.execute("SELECT dependants FROM employees WHERE id=?", (eid,)).fetchone()[0]
        for back in range(6, 0, -1):
            y, m = today.year, today.month - back
            while m <= 0:
                y, m = y - 1, m + 12
            period_end = date(y, m, 28)
            if period_end < hire or (term_date and date(y, m, 1) > date.fromisoformat(term_date)):
                continue
            overtime = rng.choice([0, 0, 0, 1, 2, 3]) * 800_000 if level <= 3 else 0
            bonus = int(current * rng.uniform(0.3, 1.0) / 100_000) * 100_000 if m in (3, 6, 9, 12) else 0
            slip = build_payslip(current, allowance, overtime, bonus, dependants)
            conn.execute("INSERT INTO payslips VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
                         (eid, f"{y}-{m:02d}", *slip.values()))
        # leave
        if not terminated:
            seniority = (today - hire).days // (365 * 5)
            entitled = 12 + seniority
            carried = rng.choice([0, 0, 1, 2, 3])
            used = min(entitled, rng.choice([0, 1, 2, 3, 4, 5, 6, 8]))
            sick = rng.choice([0, 0, 1, 2])
            conn.execute("INSERT INTO leave_balances VALUES (?,?,?,?,?,?)",
                         (eid, today.year, entitled, carried, used, sick))
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
                conn.execute("INSERT INTO leave_requests(employee_id, start_date, end_date, days, leave_type, reason, status, approver_id, created_at) VALUES (?,?,?,?,?,?,?,?,?)",
                             (eid, start.isoformat(), end.isoformat(), days, "annual", "Việc cá nhân", "approved",
                              manager_id, (start - timedelta(days=7)).isoformat()))
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
            conn.execute("UPDATE employees SET title=? WHERE id=?", (f"Trưởng đơn vị - {name}", eid))
        unit_head[code] = eid
        conn.execute("INSERT INTO org_units VALUES (?,?,?,?,?)", (code, name, typ, parent, eid))

    persona_ids: dict[str, int] = {p["key"]: unit_head[p["head_of"]] for p in PERSONAS if p.get("head_of")}
    for p in PERSONAS:
        if p.get("unit"):
            persona_ids[p["key"]] = new_employee(p["unit"], p["level"], unit_head[p["unit"]], p)
    for unit, size in TEAM_SIZES.items():
        existing = conn.execute("SELECT COUNT(*) FROM employees WHERE unit_code=? AND id<>?",
                                (unit, unit_head[unit])).fetchone()[0]
        for _ in range(max(0, size - existing)):
            new_employee(unit, rng.choices([1, 2, 3, 4], weights=[2, 4, 3, 1])[0], unit_head[unit])
        for _ in range(rng.choice([0, 1, 1, 2])):  # leavers during the last 12 months
            new_employee(unit, rng.choice([1, 2, 3]), unit_head[unit], terminated=True)

    for p in PERSONAS:
        for role, scope in p["roles"]:
            conn.execute("INSERT INTO role_assignments VALUES (?,?,?)", (persona_ids[p["key"]], role, scope))

    # a few upcoming approved leaves in Studio Alpha (team calendar demo)
    alpha = [r[0] for r in conn.execute("SELECT id FROM employees WHERE unit_code='SMG-ALPHA' AND status='active'")]
    for eid, (offset, days, typ) in zip(alpha[1:4], [(3, 2, "annual"), (6, 1, "sick"), (10, 3, "annual")]):
        start = today + timedelta(days=offset)
        while start.weekday() >= 5:
            start += timedelta(days=1)
        end = start
        while workdays(start, end) < days:
            end += timedelta(days=1)
        conn.execute("INSERT INTO leave_requests(employee_id, start_date, end_date, days, leave_type, reason, status, approver_id, created_at) VALUES (?,?,?,?,?,?,?,?,?)",
                     (eid, start.isoformat(), end.isoformat(), days, typ,
                      "Khám bệnh" if typ == "sick" else "Việc gia đình", "approved", unit_head["SMG-ALPHA"], today.isoformat()))

    # budgets (VND) for BU / function / department units, Jan .. current month
    for code, _name, typ, _parent in ORG:
        if typ not in ("bu", "function", "department"):
            continue
        scale = {"bu": 3.0, "function": 1.0, "department": 1.4}[typ]
        for m in range(1, today.month + 1):
            for cat, base in [("Nhân sự", 2500), ("Marketing", 900), ("Hạ tầng & cloud", 700), ("Công tác & đào tạo", 120)]:
                planned = int(base * scale * rng.uniform(0.8, 1.2)) * 1_000_000
                actual = int(planned * rng.gauss(1.0, 0.12) / 1_000_000) * 1_000_000 if m < today.month else int(planned * 0.55)
                conn.execute("INSERT INTO budgets VALUES (?,?,?,?,?)", (code, f"{today.year}-{m:02d}", cat, planned, actual))
    conn.commit()
    conn.close()


# --------------------------------------------------------------------------- org helpers
class Org:
    """In-memory snapshot of the org tree for fast scope computations."""

    def __init__(self) -> None:
        conn = connect()
        self.units = {r["code"]: dict(r) for r in conn.execute("SELECT * FROM org_units")}
        self.employees = {r["id"]: dict(r) for r in conn.execute(
            "SELECT id, emp_code, email, full_name, title, level, unit_code, manager_id, location, hire_date, status, "
            "termination_date FROM employees")}
        conn.close()
        self.children: dict[str, list[str]] = {}
        for code, u in self.units.items():
            if u["parent_code"]:
                self.children.setdefault(u["parent_code"], []).append(code)
        self.reports: dict[int, list[int]] = {}
        for e in self.employees.values():
            if e["manager_id"]:
                self.reports.setdefault(e["manager_id"], []).append(e["id"])
        self.by_email = {e["email"]: e["id"] for e in self.employees.values()}
        self.by_code = {e["emp_code"].lower(): e["id"] for e in self.employees.values()}

    def descendants(self, unit: str) -> set[str]:
        out, stack = set(), [unit]
        while stack:
            u = stack.pop()
            if u in out:
                continue
            out.add(u)
            stack.extend(self.children.get(u, []))
        return out

    def ancestors(self, unit: str) -> list[str]:
        path = []
        while unit:
            path.append(unit)
            unit = self.units[unit]["parent_code"]
        return list(reversed(path))  # root first

    def bu_of(self, unit: str) -> str:
        path = self.ancestors(unit)
        return path[1] if len(path) > 1 else path[0]

    def department_of(self, unit: str) -> str:
        path = self.ancestors(unit)
        return path[2] if len(path) > 2 else path[-1]

    def reporting_subtree(self, emp_id: int) -> set[int]:
        out, stack = set(), list(self.reports.get(emp_id, []))
        while stack:
            e = stack.pop()
            if e in out:
                continue
            out.add(e)
            stack.extend(self.reports.get(e, []))
        return out

    def employees_in_units(self, units: set[str]) -> set[int]:
        return {e["id"] for e in self.employees.values() if e["unit_code"] in units}

    def resolve(self, ref: str | None) -> int | None:
        """email / emp_code / exact or partial full name → employee id (None if ambiguous/unknown)."""
        if not ref:
            return None
        ref = ref.strip()
        if ref.lower() in self.by_code:
            return self.by_code[ref.lower()]
        if "@" in ref:
            return self.by_email.get(ref.lower())
        from .rag.text import strip_accents
        q = strip_accents(ref).lower()
        hits = [e["id"] for e in self.employees.values() if strip_accents(e["full_name"]).lower() == q]
        if len(hits) == 1:
            return hits[0]
        hits = [e["id"] for e in self.employees.values() if q in strip_accents(e["full_name"]).lower()]
        return hits[0] if len(hits) == 1 else None


_org: Org | None = None


def get_org() -> Org:
    global _org
    if _org is None:
        _org = Org()
    return _org


def reset_org_cache() -> None:
    global _org
    _org = None
