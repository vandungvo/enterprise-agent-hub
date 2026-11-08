"""HRIS package: demo enterprise systems of record: HRIS (org, employees), payroll, time & leave, finance.

Everything here is synthetic data for a FICTIONAL group ("Sao Mai Group") shaped like a large
Vietnamese tech conglomerate (several business units + corporate functions). In production this
module is replaced by connectors to the real HRIS / payroll / ERP (read through service accounts),
while app/access/policy.py and the tools keep enforcing access exactly the same way.
"""
from app.hris.demo_data import EMAIL_DOMAIN, PERSONAS, seed_hris
from app.hris.org import GROUP_UNIT, Org, get_org, reset_org_cache
from app.hris.payroll import (
    DEPENDANT_DEDUCTION,
    INSURANCE_CAP,
    PERSONAL_DEDUCTION,
    SI_RATE,
    build_payslip,
    compute_pit,
    workdays,
)
from app.hris.queries import employees_with_role, fetch_all, fetch_one, fetch_value
from app.hris.schema import (
    budgets,
    compensation,
    employees,
    expense_claims,
    leave_balances,
    leave_requests,
    org_units,
    payslips,
    role_assignments,
    tickets,
)

__all__ = [
    "DEPENDANT_DEDUCTION", "EMAIL_DOMAIN", "GROUP_UNIT", "INSURANCE_CAP", "PERSONAL_DEDUCTION", "PERSONAS", "SI_RATE",
    "Org", "budgets", "build_payslip", "compensation", "compute_pit", "employees", "employees_with_role",
    "expense_claims", "fetch_all", "fetch_one", "fetch_value", "get_org", "leave_balances", "leave_requests",
    "org_units", "payslips", "reset_org_cache", "role_assignments", "seed_hris", "tickets", "workdays",
]
