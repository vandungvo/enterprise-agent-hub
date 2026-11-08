"""Org tree snapshot (units, reporting lines) cached per process with a TTL."""
from __future__ import annotations

import time

from app.core.settings import settings
from app.hris.queries import fetch_all

GROUP_UNIT = "SMG-GROUP"

class Org:
    """In-memory snapshot of the org tree for fast scope computations."""

    def __init__(self) -> None:
        self.units = {r["code"]: r for r in fetch_all(
            "SELECT code, name, type, parent_code, head_employee_id FROM org_units")}
        self.employees = {r["id"]: r for r in fetch_all(
            "SELECT id, emp_code, email, full_name, title, level, unit_code, manager_id, location, hire_date, status, "
            "termination_date FROM employees ORDER BY id")}
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
        from app.rag.text import strip_accents
        q = strip_accents(ref).lower()
        hits = [e["id"] for e in self.employees.values() if strip_accents(e["full_name"]).lower() == q]
        if len(hits) == 1:
            return hits[0]
        hits = [e["id"] for e in self.employees.values() if q in strip_accents(e["full_name"]).lower()]
        return hits[0] if len(hits) == 1 else None


_org: Org | None = None
_org_loaded_at = 0.0


def get_org() -> Org:
    """Org snapshot shared by all requests of this process; refreshed every ORG_CACHE_TTL seconds so HRIS
    changes (new hires, transfers, terminations) reach every server instance without a restart."""
    global _org, _org_loaded_at
    if _org is None or time.monotonic() - _org_loaded_at > settings.org_cache_ttl:
        _org, _org_loaded_at = Org(), time.monotonic()
    return _org


def reset_org_cache() -> None:
    global _org
    _org = None
