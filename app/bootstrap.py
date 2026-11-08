"""Process bootstrap: schema migrations, demo accounts, HRIS data and KB documents (idempotent) + retention purge."""
from __future__ import annotations

import logging

import yaml
from sqlalchemy import func, select

from app import hris
from app.access.auth import hash_password
from app.agents.conversation import purge_expired_conversations
from app.agents.registry import get_platform
from app.core.db import SessionLocal, seed_lock
from app.core.migrations import migrate
from app.core.settings import settings
from app.models import Document, User
from app.rag import knowledge

log = logging.getLogger("agenthub.seed")
DEMO_PASSWORD = "demo123"


def parse_front_matter(text: str) -> tuple[dict, str]:
    if text.startswith("---"):
        _, fm, body = text.split("---", 2)
        return yaml.safe_load(fm) or {}, body.lstrip()
    return {}, text


def seed() -> None:
    """Idempotent bootstrap: schema migrations, demo HRIS, demo accounts, KB documents, retention purge.
    Runs at every process start; the lock makes concurrent cold starts (serverless) safe."""
    with seed_lock():
        _seed()


def _seed() -> None:
    migrate()
    hris.seed_hris()
    hris.reset_org_cache()
    with SessionLocal() as db:
        if not db.scalar(select(func.count()).select_from(User)):
            db.add_all(User(email=p["email"], password_hash=hash_password(DEMO_PASSWORD)) for p in hris.PERSONAS)
            db.commit()
            log.info("Seeded %d demo accounts (password: %s)", len(hris.PERSONAS), DEMO_PASSWORD)
        has_docs = bool(db.scalar(select(func.count()).select_from(Document)))

    if not has_docs and settings.seed_docs_dir.exists():
        platform = get_platform()
        for kb_dir in sorted(settings.seed_docs_dir.iterdir()):
            if not kb_dir.is_dir() or kb_dir.name not in platform.knowledge_bases:
                continue
            for f in sorted(kb_dir.glob("*.md")):
                meta, body = parse_front_matter(f.read_text(encoding="utf-8"))
                acl = {k: meta[k] for k in ("roles", "units", "min_level") if meta.get(k)}
                knowledge.ingest(kb_dir.name, f.name, body.encode("utf-8"), title=meta.get("title"),
                                 classification=meta.get("classification", "internal"), acl=acl)
    purge_expired_conversations()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    seed()
