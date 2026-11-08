"""Demo token auth. In production: SSO (Azure AD / Google Workspace / Keycloak) via OIDC;
the IdP email maps to the HRIS employee record, which is the source of org attributes and roles."""
from __future__ import annotations

import base64
import hashlib
import hmac
import json
import secrets
from datetime import UTC, datetime, timedelta

from fastapi import Depends, Header, HTTPException
from sqlalchemy import delete, func, select

from app.access import Principal, principal_for
from app.core.db import SessionLocal, utcnow
from app.core.settings import settings
from app.models import LoginFailure, User

_ITER = 200_000


def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), _ITER).hex()
    return f"pbkdf2${salt}${digest}"


def verify_password(password: str, stored: str) -> bool:
    try:
        _, salt, digest = stored.split("$")
    except ValueError:
        return False
    candidate = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), _ITER).hex()
    return hmac.compare_digest(candidate, digest)


def _b64(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()


def _unb64(text: str) -> bytes:
    return base64.urlsafe_b64decode(text + "=" * (-len(text) % 4))


def _sign(payload: str) -> str:
    return _b64(hmac.new(settings.session_secret, payload.encode(), hashlib.sha256).digest())


def login_throttled(email: str) -> bool:
    """Too many recent failures for this account? Counted in the shared DB, so the limit holds across instances."""
    since = utcnow() - timedelta(minutes=settings.login_window_minutes)
    with SessionLocal() as db:
        failures = db.scalar(select(func.count()).select_from(LoginFailure)
                             .where(LoginFailure.email == email, LoginFailure.created_at >= since))
    return failures >= settings.login_max_failures


def record_login_failure(email: str) -> None:
    with SessionLocal() as db:
        db.add(LoginFailure(email=email))
        db.commit()


def clear_login_failures(email: str) -> None:
    with SessionLocal() as db:
        db.execute(delete(LoginFailure).where(LoginFailure.email == email))
        db.commit()


def create_session(user: User) -> str:
    """Stateless signed token (email + expiry, HMAC-SHA256). Any server instance can verify it without a
    session table, which matters on serverless hosts where each instance has its own local database."""
    exp = int((utcnow() + timedelta(hours=settings.session_hours)).replace(tzinfo=UTC).timestamp())
    payload = _b64(json.dumps({"email": user.email, "exp": exp}, separators=(",", ":")).encode())
    return f"{payload}.{_sign(payload)}"


def principal_from_token(token: str | None) -> Principal | None:
    if not token or token.count(".") != 1:
        return None
    payload, sig = token.split(".")
    if not hmac.compare_digest(sig, _sign(payload)):
        return None
    try:
        claims = json.loads(_unb64(payload))
    except ValueError:
        return None
    if claims.get("exp", 0) < datetime.now(UTC).timestamp():
        return None
    with SessionLocal() as db:
        user = db.scalar(select(User).where(User.email == claims.get("email")))
    # Re-derived on every request: role or org changes in the HRIS apply immediately,
    # and terminated employees lose access.
    return principal_for(user.email, user.id) if user else None


def current_principal(authorization: str | None = Header(default=None)) -> Principal:
    token = authorization.removeprefix("Bearer ").strip() if authorization else None
    p = principal_from_token(token)
    if p is None:
        raise HTTPException(status_code=401, detail="Chưa đăng nhập hoặc phiên đã hết hạn")
    return p


def require_any_role(*roles: str):
    def dep(p: Principal = Depends(current_principal)) -> Principal:
        if not set(roles) & p.roles:
            raise HTTPException(status_code=403, detail="Không đủ quyền")
        return p

    return dep
