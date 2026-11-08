from datetime import date

from fastapi.testclient import TestClient

from app import hris
from app.db import PendingAction, SessionLocal
from app.main import app
from tests.helpers import P

client = TestClient(app)


def login(key):
    r = client.post("/api/login", json={"email": f"{key}@saomai.vn", "password": "demo123"})
    assert r.status_code == 200, r.text
    return {"Authorization": f"Bearer {r.json()['token']}"}


def test_login_and_me():
    assert client.post("/api/login", json={"email": "ceo@saomai.vn", "password": "x"}).status_code == 401
    me = client.get("/api/me", headers=login("dev.alpha")).json()
    perms = {x["resource"]: x["scope"] for x in me["permissions"]}
    assert perms["compensation.individual"] == "Chỉ bản thân"
    assert perms["workforce.aggregate"] == "Không"
    assert client.get("/api/me").status_code == 401


def test_role_gated_endpoints():
    dev = login("dev.alpha")
    assert client.get("/api/metrics", headers=dev).status_code == 403
    assert client.get("/api/admin/agents", headers=dev).status_code == 403
    assert client.get("/api/audit/data-access", headers=dev).status_code == 403
    assert client.get("/api/kbs/leadership/documents", headers=dev).status_code == 403
    it = login("itadmin")
    assert client.get("/api/admin/agents", headers=it).status_code == 200
    assert client.get("/api/audit/data-access", headers=it).status_code == 403  # admin ≠ auditor
    assert client.get("/api/audit/data-access", headers=login("chro")).status_code == 200


def test_restricted_document_titles_invisible():
    docs = client.get("/api/kbs/leadership/documents", headers=login("manager.alpha")).json()
    assert all(d["classification"] != "restricted" for d in docs)
    docs_ceo = client.get("/api/kbs/leadership/documents", headers=login("ceo")).json()
    assert any(d["classification"] == "restricted" for d in docs_ceo)


def test_kb_upload_permissions():
    files = {"file": ("x.md", "# Quy định A\n\nNội dung thử".encode(), "text/markdown")}
    assert client.post("/api/kbs/people_policy/documents", headers=login("dev.alpha"), files=files).status_code == 403
    r = client.post("/api/kbs/people_policy/documents", headers=login("hrbp.games"), files=files,
                    data={"classification": "confidential", "roles": "manager"})
    assert r.status_code == 200


def test_leave_approval_routed_to_direct_manager():
    dev, mgr = P("dev.alpha"), P("manager.alpha")
    year = date.today().year
    with SessionLocal() as db:
        a = PendingAction(tool="submit_leave_request", summary="test", requested_by=dev.employee_id,
                          requester_name=dev.full_name, department=dev.bu_code, agent_id="people",
                          approver_ids=[mgr.employee_id],
                          payload={"start_date": f"{year}-12-29", "end_date": f"{year}-12-29",
                                   "leave_type": "annual", "reason": "test"})
        db.add(a)
        db.commit()
        action_id = a.id
    conn = hris.connect()
    used_before = conn.execute("SELECT used FROM leave_balances WHERE employee_id=?", (dev.employee_id,)).fetchone()[0]
    conn.close()

    assert client.post(f"/api/approvals/{action_id}/decision", headers=login("dev.alpha"), json={"approve": True}).status_code == 403
    assert client.post(f"/api/approvals/{action_id}/decision", headers=login("head.games"), json={"approve": True}).status_code == 403
    assert client.post(f"/api/approvals/{action_id}/decision", headers=login("itadmin"), json={"approve": True}).status_code == 403

    h = login("manager.alpha")
    assert any(x["id"] == action_id for x in client.get("/api/approvals?scope=review", headers=h).json())
    assert client.post(f"/api/approvals/{action_id}/decision", headers=h, json={"approve": True}).json()["status"] == "executed"
    assert client.post(f"/api/approvals/{action_id}/decision", headers=h, json={"approve": True}).status_code == 409
    conn = hris.connect()
    used_after = conn.execute("SELECT used FROM leave_balances WHERE employee_id=?", (dev.employee_id,)).fetchone()[0]
    conn.close()
    d = date(year, 12, 29)
    assert used_after - used_before == hris.workdays(d, d)


def test_my_data_access_shows_who_viewed_me():
    from tests.helpers import run_tool
    run_tool("cnb", "get_payslip", employee="newbie@saomai.vn")
    log = client.get("/api/my-data-access", headers=login("newbie")).json()
    assert any(r["actor"] == P("cnb").full_name and r["resource"] == "compensation.individual" for r in log)


def test_usage_metrics_scope():
    assert client.get("/api/metrics", headers=login("ceo")).json()["scope"] == "Toàn tập đoàn"
    assert client.get("/api/metrics", headers=login("head.games")).json()["scope"] == "Sao Mai Games"
