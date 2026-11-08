"""Schema migrations: no drift between models and migrations; legacy (create_all) databases are adopted."""
import tempfile
from pathlib import Path

from alembic.autogenerate import compare_metadata
from alembic.runtime.migration import MigrationContext
from sqlalchemy import create_engine, insert, inspect, select, text

from app.core.db import engine
from app.core.migrations import current_revision, migrate
from app.models import PendingAction, PendingActionApprover, all_metadata


def test_migrations_match_models():
    """`alembic revision --autogenerate` would produce nothing: every model change has a migration."""
    with engine.connect() as conn:
        diff = compare_metadata(MigrationContext.configure(conn, opts={"compare_type": True}), all_metadata())
    assert diff == [], f"models and migrations differ, add a migration: {diff}"


def test_adopts_pre_migration_database():
    db_file = Path(tempfile.mkdtemp(prefix="agenthub-legacy-")) / "legacy.db"
    legacy = create_engine(f"sqlite:///{db_file.as_posix()}")
    migrate(legacy, revision="0001")                      # schema as it was before migrations existed...
    with legacy.begin() as conn:
        conn.execute(text("DROP TABLE alembic_version"))  # ...created by create_all, so no version table
        conn.execute(insert(PendingAction.__table__).values(
            id=7, tool="create_ticket", payload={}, summary="x", requested_by=1, requester_name="A", department="IT",
            approver_ids=[3, 5], agent_id="it_helpdesk", status="pending"))

    migrate(legacy)

    assert current_revision(legacy) == "0002"
    assert "pending_action_approvers" in inspect(legacy).get_table_names()
    with legacy.connect() as conn:  # approver JSON was backfilled into the normalized table
        rows = conn.execute(select(PendingActionApprover.action_id, PendingActionApprover.employee_id)).all()
    assert sorted(rows) == [(7, 3), (7, 5)]
    legacy.dispose()
