"""Authorization invariants. These are the tests that matter most for an enterprise rollout."""
import json

import pytest
from sqlalchemy import select

from app.db import DataAccessLog, SessionLocal
from app.rag import knowledge
from app.registry import get_platform
from tests.helpers import P, denied, run_tool

DEV, MGR = "dev.alpha@saomai.vn", "manager.alpha@saomai.vn"


# ---------------------------------------------------------------- salary (restricted)
def test_everyone_sees_own_payslip():
    for key in ("dev.alpha", "manager.alpha", "itadmin"):
        out = json.loads(run_tool(key, "get_payslip"))
        assert out["employee"] == P(key).full_name
    assert "Chưa có phiếu lương" in run_tool("newbie", "get_payslip")  # joined 9 days ago


@pytest.mark.parametrize("viewer", ["dev.alpha", "manager.alpha", "head.games", "hrbp.games", "itadmin", "cfo", "ceo"])
def test_individual_salary_of_staff_is_hidden_from(viewer):
    """Managers, BU heads, HRBP, CFO, CEO and IT admins never see a staff member's salary."""
    assert denied(viewer, "get_payslip", employee=DEV if viewer != "dev.alpha" else MGR)


@pytest.mark.parametrize("viewer", ["cnb", "chro"])
def test_cnb_and_chro_see_individual_salary(viewer):
    assert json.loads(run_tool(viewer, "get_payslip", employee=DEV))["employee"] == P("dev.alpha").full_name


def test_ceo_sees_salary_of_direct_reports_only():
    assert not denied("ceo", "get_compensation_history", employee="head.games@saomai.vn")
    assert denied("ceo", "get_compensation_history", employee=MGR)


def test_identity_claims_in_input_do_not_matter():
    # The tool has no way to pass "I am the CEO": identity comes only from the session principal.
    assert denied("dev.alpha", "get_payslip", employee="ceo@saomai.vn")
    assert denied("dev.alpha", "get_payslip", employee="Lê Hoàng Minh")


def test_denials_are_audited():
    denied("newbie", "get_payslip", employee=DEV)
    with SessionLocal() as db:
        row = db.scalars(select(DataAccessLog).where(DataAccessLog.actor_employee_id == P("newbie").employee_id,
                                                     DataAccessLog.allowed.is_(False))).first()
    assert row is not None and row.resource == "compensation.individual"


# ---------------------------------------------------------------- profile & leave
def test_profile_sections_are_masked():
    out = json.loads(run_tool("dev.alpha", "get_employee_profile", employee=MGR))
    assert "public" in out and "personal" not in out and "employment" not in out
    mgr_view = json.loads(run_tool("manager.alpha", "get_employee_profile", employee=DEV))
    assert "employment" in mgr_view and "personal" not in mgr_view  # manager: no national id / dob
    hrbp_view = json.loads(run_tool("hrbp.games", "get_employee_profile", employee=DEV))
    assert "personal" in hrbp_view


def test_hrbp_is_limited_to_own_business_unit():
    pay_employee = next(e["email"] for e in P("ceo").org.employees.values()
                        if e["unit_code"] == "SMP-CORE" and e["status"] == "active")
    assert denied("hrbp.games", "get_leave_balance", employee=pay_employee)
    assert not denied("hrbp.games", "get_leave_balance", employee=DEV)


def test_team_calendar_hides_leave_type_from_peers():
    peer = json.loads(run_tool("dev.alpha", "team_calendar", start_date="2026-01-01", end_date="2026-02-28"))
    others = [a for a in peer["absences"] if a["employee"] != P("dev.alpha").full_name]
    assert all(a["type"] == "vắng mặt" for a in others)


# ---------------------------------------------------------------- aggregates
def test_small_groups_are_suppressed_for_managers():
    out = json.loads(run_tool("manager.alpha", "workforce_analytics", agent="insights",
                              metric="avg_base_salary", group_by="level"))
    assert out["privacy"]["min_group_size"] == 5
    for row in out["rows"]:
        assert row["suppressed"] == (row["employees"] < 5) or "ẩn bổ sung" in " ".join(out["privacy"]["suppressed_groups"])
        if row["employees"] < 5:
            assert row["value"] is None


def test_complementary_suppression():
    out = json.loads(run_tool("ceo", "workforce_analytics", agent="insights", metric="payroll_cost", group_by="bu"))
    hidden = [r for r in out["rows"] if r["suppressed"]]
    assert len(hidden) != 1  # a single hidden group could be recovered from total - others


def test_aggregates_limited_to_scope():
    assert denied("head.games", "workforce_analytics", agent="insights", metric="headcount", unit_code="SMP")
    assert denied("dev.alpha", "workforce_analytics", agent="insights", metric="headcount")
    assert denied("itadmin", "workforce_analytics", agent="insights", metric="payroll_cost")
    out = json.loads(run_tool("ceo", "workforce_analytics", agent="insights", metric="headcount", group_by="bu"))
    assert out["scope"] == "Toàn tập đoàn"


def test_budget_scope():
    assert denied("dev.alpha", "budget_report", agent="finance")
    assert denied("finance.pay", "budget_report", agent="finance", unit_code="SMG")
    out = json.loads(run_tool("finance.pay", "budget_report", agent="finance"))
    assert [r["unit_code"] for r in out["reports"]] == ["SMP"]


# ---------------------------------------------------------------- platform roles & documents
def test_platform_admin_has_no_hr_data_access():
    assert denied("itadmin", "get_payslip", employee=DEV)
    assert denied("itadmin", "get_leave_balance", employee=DEV)
    assert "insights" not in {a.id for a in get_platform().agents_for(P("itadmin"))}


def test_document_acl_filters_rag():
    def titles(key):
        return {h["doc_title"] for h in knowledge.search("chiến lược 2027 mục tiêu tăng trưởng", ["leadership"], 10, principal=P(key))}
    assert any("chiến lược" in t.lower() for t in titles("ceo"))
    assert not any("chiến lược" in t.lower() for t in titles("manager.alpha"))  # manager, not exec
    assert titles("dev.alpha") == set()  # leadership KB docs require manager+


def test_agent_access_by_role():
    pl = get_platform()
    assert "insights" in {a.id for a in pl.agents_for(P("manager.alpha"))}
    assert "insights" not in {a.id for a in pl.agents_for(P("dev.alpha"))}
