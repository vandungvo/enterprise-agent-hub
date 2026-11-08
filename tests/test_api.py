from datetime import date

from fastapi.testclient import TestClient

from app import hris
from app.core.db import SessionLocal
from app.main import app
from app.models import PendingAction, PendingActionApprover
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


def test_session_token_is_signed_and_stateless():
    """Tokens verify without server-side state (serverless instances do not share a DB) and cannot be forged."""
    import base64
    import json

    token = login("dev.alpha")["Authorization"].removeprefix("Bearer ")
    payload, sig = token.split(".")
    assert json.loads(base64.urlsafe_b64decode(payload + "==="))["email"] == "dev.alpha@saomai.vn"
    forged = base64.urlsafe_b64encode(json.dumps({"email": "ceo@saomai.vn", "exp": 9999999999}).encode())
    for bad in (f"{payload}.{sig[:-2]}AA", f"{forged.decode().rstrip('=')}.{sig}", "garbage"):
        assert client.get("/api/me", headers={"Authorization": f"Bearer {bad}"}).status_code == 401


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
        db.flush()
        db.add(PendingActionApprover(action_id=a.id, employee_id=mgr.employee_id))
        db.commit()
        action_id = a.id
    used_before = hris.fetch_value("SELECT used FROM leave_balances WHERE employee_id = :eid AND year = :y", eid=dev.employee_id, y=year)

    assert client.post(f"/api/approvals/{action_id}/decision", headers=login("dev.alpha"), json={"approve": True}).status_code == 403
    assert client.post(f"/api/approvals/{action_id}/decision", headers=login("head.games"), json={"approve": True}).status_code == 403
    assert client.post(f"/api/approvals/{action_id}/decision", headers=login("itadmin"), json={"approve": True}).status_code == 403

    h = login("manager.alpha")
    assert any(x["id"] == action_id for x in client.get("/api/approvals?scope=review", headers=h).json())
    assert client.post(f"/api/approvals/{action_id}/decision", headers=h, json={"approve": True}).json()["status"] == "executed"
    assert client.post(f"/api/approvals/{action_id}/decision", headers=h, json={"approve": True}).status_code == 409
    used_after = hris.fetch_value("SELECT used FROM leave_balances WHERE employee_id = :eid AND year = :y", eid=dev.employee_id, y=year)
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


def test_health_reports_database():
    r = client.get("/api/health")
    assert r.status_code == 200 and r.json()["database_ok"] is True


def test_knowledge_index_picks_up_writes_from_other_instances():
    """Another server instance writes chunks straight to the shared DB (no local invalidate()):
    the next search on this instance must rebuild its in-memory index and find them."""
    from app.models import Chunk, Document
    from app.rag import knowledge

    knowledge.search("warmup", ["company"], principal=P("dev.alpha"))  # build + cache the index
    with SessionLocal() as db:
        doc = Document(kb_id="company", title="Quy chế bãi đỗ xe", filename="parking.md", num_chunks=1)
        db.add(doc)
        db.flush()
        db.add(Chunk(document_id=doc.id, kb_id="company", ordinal=0, heading="Bãi đỗ xe",
                     text="Nhân viên gửi xe máy miễn phí tại tầng hầm B2 tòa Sao Mai."))
        db.commit()
    hits = knowledge.search("gửi xe tầng hầm", ["company"], principal=P("dev.alpha"))
    assert any(h["doc_title"] == "Quy chế bãi đỗ xe" for h in hits)
    knowledge.delete_document(doc.id)
