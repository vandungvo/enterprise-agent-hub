"""Schema migrations (Alembic), applied programmatically.

`migrate()` runs at startup inside `seed_lock()`, so exactly one instance upgrades the schema while the
others wait. It also adopts databases created before migrations existed (by `create_all`): their schema
equals the baseline revision, so they are stamped `0001` and then upgraded normally.

CLI equivalents:  alembic upgrade head  ·  alembic revision --autogenerate -m "..."  ·  alembic current
"""
from __future__ import annotations

import logging

from alembic import command
from alembic.config import Config
from alembic.runtime.migration import MigrationContext
from sqlalchemy import Engine, inspect

from app.core.db import engine
from app.core.settings import ROOT

log = logging.getLogger("agenthub.migrations")
BASELINE_REVISION = "0001"


def alembic_config() -> Config:
    # Built in code (no alembic.ini needed at runtime: serverless bundles only include app code + migrations/).
    cfg = Config()
    cfg.set_main_option("script_location", str(ROOT / "migrations"))
    return cfg


def current_revision(bind: Engine | None = None) -> str | None:
    with (bind or engine).connect() as conn:
        return MigrationContext.configure(conn).get_current_revision()


def migrate(bind: Engine | None = None, revision: str = "head") -> None:
    bind = bind or engine
    cfg = alembic_config()
    with bind.begin() as conn:
        cfg.attributes["connection"] = conn
        tables = set(inspect(conn).get_table_names())
        if "alembic_version" not in tables and "users" in tables:
            log.info("Adopting pre-migration database: stamping baseline %s", BASELINE_REVISION)
            command.stamp(cfg, BASELINE_REVISION)
        command.upgrade(cfg, revision)
    log.info("Database schema at revision %s", current_revision(bind))
