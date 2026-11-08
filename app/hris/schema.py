"""HRIS tables (dialect-neutral SQLAlchemy Core). Dates are ISO-8601 strings; money is BigInteger VND."""
from __future__ import annotations

from sqlalchemy import BigInteger, Column, Float, Integer, String, Table, Text

from app.core.db import Base

# Dates are ISO-8601 strings (as most HRIS exports are); money is BigInteger VND.
_md = Base.metadata
org_units = Table("org_units", _md,
                  Column("code", String(40), primary_key=True), Column("name", String(200)),
                  Column("type", String(20)), Column("parent_code", String(40)),
                  Column("head_employee_id", Integer))
employees = Table("employees", _md,
                  Column("id", Integer, primary_key=True, autoincrement=False),
                  Column("emp_code", String(20), unique=True), Column("email", String(200), unique=True),
                  Column("full_name", String(200)), Column("gender", String(1)), Column("dob", String(10)),
                  Column("personal_phone", String(20)), Column("national_id", String(20)), Column("address", Text),
                  Column("dependants", Integer), Column("title", String(200)), Column("level", Integer),
                  Column("unit_code", String(40), index=True), Column("manager_id", Integer, index=True),
                  Column("location", String(50)), Column("hire_date", String(10)), Column("status", String(20)),
                  Column("termination_date", String(10)), Column("termination_reason", Text),
                  Column("performance_rating", String(1)))
role_assignments = Table("role_assignments", _md,
                         Column("employee_id", Integer, primary_key=True), Column("role", String(40), primary_key=True),
                         Column("scope_unit", String(40), primary_key=True))
compensation = Table("compensation", _md,
                     Column("id", Integer, primary_key=True, autoincrement=True),
                     Column("employee_id", Integer, index=True), Column("effective_date", String(10)),
                     Column("base_salary", BigInteger), Column("allowance", BigInteger), Column("reason", Text))
payslips = Table("payslips", _md,
                 Column("employee_id", Integer, primary_key=True), Column("period", String(7), primary_key=True),
                 *(Column(c, BigInteger) for c in ("base", "allowance", "overtime", "bonus", "gross", "social_insurance",
                                                   "health_insurance", "unemployment_insurance", "pit", "net")))
leave_balances = Table("leave_balances", _md,
                       Column("employee_id", Integer, primary_key=True), Column("year", Integer, primary_key=True),
                       Column("entitled", Float), Column("carried_over", Float), Column("used", Float),
                       Column("sick_used", Float))
leave_requests = Table("leave_requests", _md,
                       Column("id", Integer, primary_key=True, autoincrement=True),
                       Column("employee_id", Integer, index=True), Column("start_date", String(10)),
                       Column("end_date", String(10)), Column("days", Float), Column("leave_type", String(20)),
                       Column("reason", Text), Column("status", String(20)), Column("approver_id", Integer),
                       Column("created_at", String(32)))
budgets = Table("budgets", _md,
                Column("unit_code", String(40), primary_key=True), Column("period", String(7), primary_key=True),
                Column("category", String(80), primary_key=True), Column("planned", BigInteger),
                Column("actual", BigInteger))
expense_claims = Table("expense_claims", _md,
                       Column("id", Integer, primary_key=True, autoincrement=True),
                       Column("employee_id", Integer, index=True), Column("amount", BigInteger),
                       Column("category", String(40)), Column("description", Text), Column("expense_date", String(10)),
                       Column("status", String(20)), Column("approver_id", Integer), Column("created_at", String(32)))
tickets = Table("tickets", _md,
                Column("id", Integer, primary_key=True, autoincrement=True), Column("category", String(40)),
                Column("title", Text), Column("description", Text), Column("priority", String(20)),
                Column("status", String(20)), Column("requester_id", Integer), Column("created_at", String(32)))
