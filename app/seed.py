"""Seed demo accounts, HRIS data and knowledge documents (idempotent) + retention housekeeping."""
from __future__ import annotations

import logging
from datetime import timedelta

import yaml
from sqlalchemy import delete, func, select

from . import hris
from .auth import hash_password
from .db import ChatMessage, Conversation, Document, SessionLocal, User, init_db, utcnow
from .rag import knowledge
from .registry import get_platform
from .settings import settings

log = logging.getLogger("agenthub.seed")
DEMO_PASSWORD = "demo123"


def parse_front_matter(text: str) -> tuple[dict, str]:
    if text.startswith("---"):
        _, fm, body = text.split("---", 2)
        return yaml.safe_load(fm) or {}, body.lstrip()
    return {}, text


def seed() -> None:
    init_db()
    hris.seed_hris()
    hris.reset_org_cache()
    with SessionLocal() as db:
        if not db.scalar(select(func.count()).select_from(User)):
            for p in hris.PERSONAS:
                db.add(User(email=p["email"], password_hash=hash_password(DEMO_PASSWORD)))
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


def purge_expired_conversations() -> int:
    """Retention: conversations that touched restricted data are deleted after N days."""
    cutoff = utcnow() - timedelta(days=settings.sensitive_retention_days)
    with SessionLocal() as db:
        ids = list(db.scalars(select(Conversation.id).where(Conversation.sensitive.is_(True),
                                                            Conversation.updated_at < cutoff)))
        if ids:
            db.execute(delete(ChatMessage).where(ChatMessage.conversation_id.in_(ids)))
            db.execute(delete(Conversation).where(Conversation.id.in_(ids)))
            db.commit()
            log.info("Purged %d sensitive conversations past retention", len(ids))
    return len(ids)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    seed()
