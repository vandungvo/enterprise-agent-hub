"""Shared response helpers (display names, labels) for the API routers."""
from __future__ import annotations

from app import hris
from app.access import Principal

ROLE_LABELS = {
    "employee": "Nhân viên", "manager": "Quản lý (có cấp dưới)", "unit_head": "Trưởng đơn vị", "ceo": "CEO tập đoàn",
    "exec": "Ban điều hành", "chro": "Giám đốc Nhân sự", "cfo": "Giám đốc Tài chính", "cnb": "C&B",
    "hrbp": "HR Business Partner", "finance": "Kiểm soát tài chính", "it_support": "IT Support",
    "auditor": "Kiểm toán / tuân thủ", "platform_admin": "Quản trị nền tảng",
}
USAGE_VIEWERS = ("platform_admin", "exec", "chro")


def unit_name(code: str) -> str:
    return hris.get_org().units.get(code, {}).get("name", code)


def employee_name(emp_id: int | None) -> str | None:
    return hris.get_org().employees.get(emp_id, {}).get("full_name") if emp_id else None


def principal_dict(p: Principal) -> dict:
    return {"employee_id": p.employee_id, "email": p.email, "full_name": p.full_name, "title": p.title,
            "level": p.level, "unit_code": p.unit_code, "bu_code": p.bu_code,
            "unit_path": [unit_name(c) for c in p.org.ancestors(p.unit_code)]}
