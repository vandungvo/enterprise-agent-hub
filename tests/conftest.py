import os
import sys
import tempfile
from pathlib import Path

# Isolated data dir and database for every test session - must be set before `app` is imported.
# TEST_DATABASE_URL runs the same suite against PostgreSQL (e.g. postgresql://postgres@localhost:5432/agenthub_test).
_tmp = tempfile.mkdtemp(prefix="agenthub-test-")
os.environ["AGENTHUB_DATA_DIR"] = _tmp
os.environ["DATABASE_URL"] = os.environ.get("TEST_DATABASE_URL") or f"sqlite:///{Path(_tmp, 'test.db').as_posix()}"
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest  # noqa: E402

from app.bootstrap import seed  # noqa: E402


@pytest.fixture(scope="session", autouse=True)
def seeded():
    if os.environ.get("TEST_DATABASE_URL"):  # start every Postgres run from an empty schema
        from sqlalchemy import text

        from app.core.db import engine
        from app.models import all_metadata
        all_metadata().drop_all(engine)
        with engine.begin() as conn:
            conn.execute(text("DROP TABLE IF EXISTS alembic_version"))
    seed()  # applies the Alembic migrations, exactly like production startup
