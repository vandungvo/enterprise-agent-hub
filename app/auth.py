"""Demo token auth. In production: SSO (Azure AD / Google Workspace / Keycloak) via OIDC;
the IdP email maps to the HRIS employee record, which is the source of org attributes and roles."""
from __future__ import annotations

import hashlib
import hmac
import secrets
from datetime import timedelta

from fastapi import Depends, Header, HTTPException

from .db import AuthSession, SessionLocal, User, utcnow
from .policy import Principal, principal_for
from .settings import settings

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


def create_session(user: User) -> str:
    token = secrets.token_urlsafe(32)
    with SessionLocal() as db:
        db.add(AuthSession(token=token, user_id=user.id,
                           expires_at=utcnow() + timedelta(hours=settings.session_hours)))
        db.commit()
    return token


def principal_from_token(token: str | None) -> Principal | None:
    if not token:
        return None
    with SessionLocal() as db:
        sess = db.get(AuthSession, token)
        if sess is None or sess.expires_at < utcnow():
            return None
        user = db.get(User, sess.user_id)
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
