"""ORM models for platform data: accounts, conversations, RAG index, audit trails, approvals."""
from __future__ import annotations

from datetime import datetime

from sqlalchemy import (
    JSON,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    LargeBinary,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base, utcnow


class User(Base):
    """Platform login account. Identity attributes (org, level, roles) come from the HRIS."""

    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(200), unique=True)
    password_hash: Mapped[str] = mapped_column(String(300))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)


class Conversation(Base):
    __tablename__ = "conversations"
    __table_args__ = (Index("ix_conversations_user_updated", "user_id", "updated_at"),)  # sidebar listing
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
    conversation_id: Mapped[int] = mapped_column(ForeignKey("conversations.id", ondelete="CASCADE"), index=True)
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
    __table_args__ = (Index("ix_llm_calls_department_created", "department", "created_at"),)  # BU-scoped KPIs
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
    requested_by: Mapped[int] = mapped_column(Integer, index=True)  # employee id
    requester_name: Mapped[str] = mapped_column(String(200), default="")
    department: Mapped[str] = mapped_column(String(50))  # requester BU
    # employee ids allowed to decide; mirrored in pending_action_approvers for indexed "waiting for me" lookups
    approver_ids: Mapped[list] = mapped_column(JSON, default=list)
    agent_id: Mapped[str] = mapped_column(String(80))
    conversation_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="pending", index=True)  # pending|processing|executed|rejected|failed
    decided_by: Mapped[int | None] = mapped_column(Integer, nullable=True)  # employee id
    decision_note: Mapped[str | None] = mapped_column(Text, nullable=True)
    result: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
    decided_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)


class PendingActionApprover(Base):
    """Normalized approver list: answers "which requests wait for employee X" with an index, at any volume."""

    __tablename__ = "pending_action_approvers"
    action_id: Mapped[int] = mapped_column(ForeignKey("pending_actions.id", ondelete="CASCADE"), primary_key=True)
    employee_id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)


class LoginFailure(Base):
    """Failed sign-ins, shared by every instance: drives brute-force throttling (app.access.auth.login_throttled)."""

    __tablename__ = "login_failures"
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(200), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow, index=True)


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



def all_metadata():
    """Base.metadata with every table registered (platform + HRIS) - for migrations and tests."""
    import app.hris.schema  # noqa: F401  (registers the HRIS tables on Base.metadata)

    return Base.metadata
