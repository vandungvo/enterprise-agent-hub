"""Platform database (users, conversations, RAG index, audit, approvals)."""
from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import (
    JSON,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    LargeBinary,
    String,
    Text,
    create_engine,
    event,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker

from .settings import settings

engine = create_engine(settings.app_db_url, connect_args={"check_same_thread": False})


@event.listens_for(engine, "connect")
def _sqlite_pragmas(dbapi_conn, _):
    cur = dbapi_conn.cursor()
    cur.execute("PRAGMA journal_mode=WAL")
    cur.execute("PRAGMA foreign_keys=ON")
    cur.close()


SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)


def utcnow() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


class Base(DeclarativeBase):
    pass


class User(Base):
    """Platform login account. Identity attributes (org, level, roles) come from the HRIS."""

    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(200), unique=True)
    password_hash: Mapped[str] = mapped_column(String(300))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)


class AuthSession(Base):
    __tablename__ = "auth_sessions"
    token: Mapped[str] = mapped_column(String(100), primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    expires_at: Mapped[datetime] = mapped_column(DateTime)


class Conversation(Base):
    __tablename__ = "conversations"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    agent_id: Mapped[str] = mapped_column(String(80))  # entry agent (router or a specialist)
    title: Mapped[str] = mapped_column(String(300), default="Cuộc trò chuyện mới")
    # True once restricted data (salary, personal data...) entered the conversation -> shorter retention
    sensitive: Mapped[bool] = mapped_column(default=False)
    # Full Messages-API history of the entry agent, append-only (thinking blocks kept as-is).
    api_messages: Mapped[list] = mapped_column(JSON, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)


class ChatMessage(Base):
    """Display-oriented copy of the conversation for the UI."""

    __tablename__ = "chat_messages"
    id: Mapped[int] = mapped_column(primary_key=True)
    conversation_id: Mapped[int] = mapped_column(ForeignKey("conversations.id", ondelete="CASCADE"))
    role: Mapped[str] = mapped_column(String(20))  # user | assistant
    content: Mapped[str] = mapped_column(Text)
    sources: Mapped[list] = mapped_column(JSON, default=list)
    trace: Mapped[list] = mapped_column(JSON, default=list)
    feedback: Mapped[int | None] = mapped_column(Integer, nullable=True)  # 1 / -1
    feedback_comment: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)


class Document(Base):
    __tablename__ = "documents"
    id: Mapped[int] = mapped_column(primary_key=True)
    kb_id: Mapped[str] = mapped_column(String(80), index=True)
    title: Mapped[str] = mapped_column(String(300))
    filename: Mapped[str] = mapped_column(String(300))
    classification: Mapped[str] = mapped_column(String(20), default="internal")
    # Document-level ACL: {"roles": [...], "units": [...], "min_level": int}; empty = everyone with KB access
    acl: Mapped[dict] = mapped_column(JSON, default=dict)
    uploaded_by: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    num_chunks: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)


class Chunk(Base):
    __tablename__ = "chunks"
    id: Mapped[int] = mapped_column(primary_key=True)
    document_id: Mapped[int] = mapped_column(ForeignKey("documents.id", ondelete="CASCADE"), index=True)
    kb_id: Mapped[str] = mapped_column(String(80), index=True)
    ordinal: Mapped[int] = mapped_column(Integer)
    heading: Mapped[str] = mapped_column(String(500), default="")
    text: Mapped[str] = mapped_column(Text)
    embedding: Mapped[bytes | None] = mapped_column(LargeBinary, nullable=True)


class LLMCall(Base):
    __tablename__ = "llm_calls"
    id: Mapped[int] = mapped_column(primary_key=True)
    conversation_id: Mapped[int | None] = mapped_column(Integer, nullable=True, index=True)
    user_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    department: Mapped[str] = mapped_column(String(50), default="")
    agent_id: Mapped[str] = mapped_column(String(80))
    model: Mapped[str] = mapped_column(String(80))
    input_tokens: Mapped[int] = mapped_column(Integer, default=0)
    output_tokens: Mapped[int] = mapped_column(Integer, default=0)
    cache_read_tokens: Mapped[int] = mapped_column(Integer, default=0)
    cache_write_tokens: Mapped[int] = mapped_column(Integer, default=0)
    cost_usd: Mapped[float] = mapped_column(Float, default=0.0)
    latency_ms: Mapped[int] = mapped_column(Integer, default=0)
    stop_reason: Mapped[str] = mapped_column(String(40), default="")
    request_id: Mapped[str] = mapped_column(String(100), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow, index=True)


class ToolCall(Base):
    __tablename__ = "tool_calls"
    id: Mapped[int] = mapped_column(primary_key=True)
    conversation_id: Mapped[int | None] = mapped_column(Integer, nullable=True, index=True)
    user_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    agent_id: Mapped[str] = mapped_column(String(80))
    tool: Mapped[str] = mapped_column(String(80))
    input: Mapped[dict] = mapped_column(JSON, default=dict)
    output_preview: Mapped[str] = mapped_column(Text, default="")
    is_error: Mapped[bool] = mapped_column(default=False)
    latency_ms: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow, index=True)


class PendingAction(Base):
    """Side-effecting tool calls held for human approval."""

    __tablename__ = "pending_actions"
    id: Mapped[int] = mapped_column(primary_key=True)
    tool: Mapped[str] = mapped_column(String(80))
    payload: Mapped[dict] = mapped_column(JSON)
    summary: Mapped[str] = mapped_column(Text)
    requested_by: Mapped[int] = mapped_column(Integer)  # employee id
    requester_name: Mapped[str] = mapped_column(String(200), default="")
    department: Mapped[str] = mapped_column(String(50))  # requester BU
    approver_ids: Mapped[list] = mapped_column(JSON, default=list)  # employee ids allowed to decide
    agent_id: Mapped[str] = mapped_column(String(80))
    conversation_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="pending")  # pending|executed|rejected|failed
    decided_by: Mapped[int | None] = mapped_column(Integer, nullable=True)  # employee id
    decision_note: Mapped[str | None] = mapped_column(Text, nullable=True)
    result: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
    decided_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)


class DataAccessLog(Base):
    """Audit trail of access to confidential / restricted data (and every denied attempt)."""

    __tablename__ = "data_access_log"
    id: Mapped[int] = mapped_column(primary_key=True)
    actor_employee_id: Mapped[int] = mapped_column(Integer, index=True)
    actor_name: Mapped[str] = mapped_column(String(200))
    resource: Mapped[str] = mapped_column(String(80))
    classification: Mapped[str] = mapped_column(String(20))
    target_employee_id: Mapped[int | None] = mapped_column(Integer, nullable=True, index=True)
    scope: Mapped[str] = mapped_column(Text, default="")
    allowed: Mapped[bool] = mapped_column(default=True)
    audit: Mapped[str] = mapped_column(String(20), default="standard")
    conversation_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow, index=True)


def init_db() -> None:
    Base.metadata.create_all(engine)
