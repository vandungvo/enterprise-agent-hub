"""Read helpers for HRIS SQL: named parameters, list values expand into IN (...) (empty lists are fine)."""
from __future__ import annotations

from typing import Any

from sqlalchemy import bindparam, text

from app.core.db import engine


def _statement(sql: str, params: dict[str, Any]):
    """`text()` with named params; list/set/tuple values become expanding IN parameters (empty is fine)."""
    stmt = text(sql)
    expanding = [k for k, v in params.items() if isinstance(v, (list, tuple, set, frozenset))]
    if expanding:
        stmt = stmt.bindparams(*(bindparam(k, expanding=True) for k in expanding))
    return stmt, {k: (list(v) if k in expanding else v) for k, v in params.items()}


def fetch_all(sql: str, **params: Any) -> list[dict]:
    stmt, args = _statement(sql, params)
    with engine.connect() as conn:
        return [dict(r) for r in conn.execute(stmt, args).mappings()]


def fetch_one(sql: str, **params: Any) -> dict | None:
    rows = fetch_all(sql, **params)
    return rows[0] if rows else None


def fetch_value(sql: str, **params: Any) -> Any:
    stmt, args = _statement(sql, params)
    with engine.connect() as conn:
        return conn.execute(stmt, args).scalar()


def employees_with_role(role: str) -> list[int]:
    return [r["employee_id"] for r in fetch_all(
        "SELECT employee_id FROM role_assignments WHERE role = :role ORDER BY employee_id", role=role)]
