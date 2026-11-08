import os
import sys
import tempfile
from pathlib import Path

# Isolated data dir for every test session - must be set before `app` is imported.
os.environ["AGENTHUB_DATA_DIR"] = tempfile.mkdtemp(prefix="agenthub-test-")
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest  # noqa: E402

from app.seed import seed  # noqa: E402


@pytest.fixture(scope="session", autouse=True)
def seeded():
    seed()
