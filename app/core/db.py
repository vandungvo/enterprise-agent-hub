"""Database engine and session: one SQLAlchemy engine for platform data and the demo HRIS.

SQLite (default, dev/tests) or PostgreSQL (DATABASE_URL, production/serverless). All SQL in the app is
dialect-neutral (SQLAlchemy Core / ORM or `text()` with named parameters), so both run the same code.
ORM models live in app.models; HRIS tables in app.hris.schema.
"""
from __future__ import annotations

import threading
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import UTC, datetime

from sqlalchemy import (
    Engine,
    create_engine,
    event,
    text,
)
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.core.settings import settings

SEED_LOCK_KEY = 0x4A6E7448  # pg_advisory_lock key shared by every instance of this app


def _make_engine(url: str) -> Engine:
    if url.startswith("sqlite"):
        eng = create_engine(url, connect_args={"check_same_thread": False})

        @event.listens_for(eng, "connect")
        def _sqlite_pragmas(dbapi_conn, _):
            cur = dbapi_conn.cursor()
            cur.execute("PRAGMA journal_mode=WAL")
            cur.execute("PRAGMA foreign_keys=ON")
            cur.close()

        return eng
    # PostgreSQL. Small pool: serverless instances are many and short-lived; pre-ping drops connections the
    # provider closed while the instance was frozen. prepare_threshold=None keeps psycopg from using
    # server-side prepared statements, which transaction-mode poolers (Neon / PgBouncer) do not support.
    return create_engine(url, pool_size=settings.db_pool_size, max_overflow=2, pool_pre_ping=True,
                         pool_recycle=300, connect_args={"prepare_threshold": None})


engine = _make_engine(settings.database_url)
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)
_local_seed_lock = threading.Lock()


@contextmanager
def seed_lock() -> Iterator[None]:
    """Serialize seeding across processes: several serverless instances may cold-start at once."""
    if engine.dialect.name != "postgresql":
        with _local_seed_lock:
            yield
        return
    with engine.connect() as conn:
        conn.execute(text("SELECT pg_advisory_lock(:k)"), {"k": SEED_LOCK_KEY})
        try:
            yield
        finally:
            conn.execute(text("SELECT pg_advisory_unlock(:k)"), {"k": SEED_LOCK_KEY})
            conn.commit()


def ping() -> bool:
    with engine.connect() as conn:
        return conn.execute(text("SELECT 1")).scalar() == 1


def utcnow() -> datetime:
    return datetime.now(UTC).replace(tzinfo=None)


class Base(DeclarativeBase):
    pass
