"""Production hardening: correlation ids, security headers, login throttling, cron auth, error hygiene."""
from dataclasses import replace

import pytest
from fastapi.testclient import TestClient

from app.api import internal
from app.core import settings as settings_module
from app.main import app

client = TestClient(app)


def test_request_id_and_security_headers():
    r = client.get("/api/demo-users", headers={"X-Request-ID": "trace-123"})
    assert r.headers["x-request-id"] == "trace-123"
    assert r.headers["x-content-type-options"] == "nosniff"
    assert r.headers["x-frame-options"] == "DENY"
    assert "frame-ancestors 'none'" in r.headers["content-security-policy"]
    assert len(client.get("/api/demo-users").headers["x-request-id"]) == 32  # generated when absent


def test_login_is_throttled_after_repeated_failures(monkeypatch):
    from app.access import auth
    monkeypatch.setattr(auth, "settings", replace(auth.settings, login_max_failures=3))
    email = "cfo@saomai.vn"
    for _ in range(3):
        assert client.post("/api/login", json={"email": email, "password": "wrong"}).status_code == 401
    blocked = client.post("/api/login", json={"email": email, "password": "demo123"})
    assert blocked.status_code == 429 and "retry-after" in blocked.headers
    auth.clear_login_failures(email)
    assert client.post("/api/login", json={"email": email, "password": "demo123"}).status_code == 200


def test_maintenance_requires_cron_secret(monkeypatch):
    monkeypatch.setattr(internal, "settings", replace(internal.settings, cron_secret=""))
    assert client.get("/api/internal/maintenance").status_code == 404  # disabled without a secret
    monkeypatch.setattr(internal, "settings", replace(internal.settings, cron_secret="s3cret"))
    assert client.get("/api/internal/maintenance").status_code == 401
    assert client.get("/api/internal/maintenance", headers={"Authorization": "Bearer nope"}).status_code == 401
    ok = client.get("/api/internal/maintenance", headers={"Authorization": "Bearer s3cret"})
    assert ok.status_code == 200 and set(ok.json()) == {"purged_conversations", "pruned_login_failures"}


def test_unhandled_errors_do_not_leak_details(monkeypatch):
    from app.api import identity

    def boom(*_a, **_k):
        raise RuntimeError("secret internal detail")

    monkeypatch.setattr(identity, "login_throttled", boom)
    r = TestClient(app, raise_server_exceptions=False).post("/api/login", json={"email": "x@y.z", "password": "p"})
    assert r.status_code == 500
    assert "secret internal detail" not in r.text and r.json()["request_id"]


@pytest.mark.parametrize(("field", "value"), [("log_format", "xml"), ("chunk_overlap", 5000), ("max_tokens", 0)])
def test_invalid_configuration_is_rejected(field, value):
    assert replace(settings_module.settings, **{field: value}).validate()


def test_default_configuration_is_valid():
    assert settings_module.settings.validate() == []
