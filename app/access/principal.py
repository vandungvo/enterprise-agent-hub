"""The authenticated principal: who is asking, rebuilt from the HRIS on every request (never from user input)."""
from __future__ import annotations

from dataclasses import dataclass, field
from functools import cached_property

from app.hris import GROUP_UNIT, Org, fetch_all, get_org


@dataclass
class Principal:
    user_id: int            # platform account id
    employee_id: int
    email: str
    full_name: str
    title: str
    level: int
    unit_code: str
    bu_code: str
    roles: set[str]
    role_scopes: dict[str, set[str]]  # role -> scope units (as assigned)
    org: Org = field(repr=False)

    @property
    def is_platform_admin(self) -> bool:
        return "platform_admin" in self.roles

    def has(self, role: str | None) -> bool:
        return role is None or role in self.roles

    # ---- scope sets (employee ids) --------------------------------------------
    @cached_property
    def subtree(self) -> set[int]:
        return self.org.reporting_subtree(self.employee_id)

    def scope_ids(self, scope: str, role: str | None) -> set[int]:
        org = self.org
        if scope == "self":
            return {self.employee_id}
        if scope == "direct_reports":
            return set(org.reports.get(self.employee_id, []))
        if scope == "subtree":
            return self.subtree
        if scope == "same_unit":
            return {e["id"] for e in org.employees.values() if e["unit_code"] == self.unit_code}
        if scope == "group":
            return set(org.employees)
        if scope == "role_scope":
            units: set[str] = set()
            for u in self.role_scopes.get(role or "", set()):
                units |= org.descendants(u)
            return org.employees_in_units(units)
        raise ValueError(f"Unknown scope {scope}")


def principal_for(email: str, user_id: int) -> Principal | None:
    org = get_org()
    emp_id = org.by_email.get(email.lower())
    if emp_id is None:
        return None
    emp = org.employees[emp_id]
    if emp["status"] != "active":
        return None
    assigned = fetch_all("SELECT role, scope_unit FROM role_assignments WHERE employee_id = :eid", eid=emp_id)
    roles, scopes = {"employee"}, {"employee": {GROUP_UNIT}}
    for r in assigned:
        roles.add(r["role"])
        scopes.setdefault(r["role"], set()).add(r["scope_unit"])
    if org.reports.get(emp_id):
        roles.add("manager")
    headed = {code for code, u in org.units.items() if u["head_employee_id"] == emp_id}
    if headed:
        roles.add("unit_head")
        scopes["unit_head"] = headed
    return Principal(user_id=user_id, employee_id=emp_id, email=emp["email"], full_name=emp["full_name"],
                     title=emp["title"], level=emp["level"], unit_code=emp["unit_code"],
                     bu_code=org.bu_of(emp["unit_code"]), roles=roles, role_scopes=scopes, org=org)
