"""Conversation service: one user turn → orchestrated agent run → persisted result."""
from __future__ import annotations

import asyncio
import logging
import re
from collections.abc import AsyncIterator
from datetime import timedelta

from sqlalchemy import delete, select

from app.access import Principal
from app.agents.registry import get_platform
from app.agents.runtime import runtime
from app.core.db import SessionLocal, utcnow
from app.core.settings import settings
from app.models import ChatMessage, Conversation
from app.tools import ToolContext

log = logging.getLogger("agenthub.conversation")
TRACE_EVENTS = {"agent_start", "tool_call", "tool_result", "approval", "agent_end", "warning"}


class ChatError(Exception):
    pass


def _entry_agent(p: Principal, conversation: Conversation | None, agent_id: str | None):
    platform = get_platform()
    wanted = conversation.agent_id if conversation else (agent_id or "router")
    if wanted == "router":
        return next(a for a in platform.agents.values() if a.role == "router")
    agent = platform.agents.get(wanted)
    if agent is None or not agent.access.allows(p):
        raise ChatError("Bạn không có quyền dùng agent này")
    return agent


def _open_turn(p: Principal, text: str, conversation_id: int | None, agent_id: str | None):
    """Load or create the conversation and store the user message (blocking: run in a thread)."""
    with SessionLocal() as db:
        conv = None
        if conversation_id:
            conv = db.get(Conversation, conversation_id)
            if conv is None or conv.user_id != p.user_id:
                raise ChatError("Không tìm thấy cuộc trò chuyện")
        agent = _entry_agent(p, conv, agent_id)
        if conv is None:
            conv = Conversation(user_id=p.user_id, agent_id=agent.id, title=text.strip()[:80] or "Cuộc trò chuyện mới",
                                api_messages=[])
            db.add(conv)
            db.flush()
        db.add(ChatMessage(conversation_id=conv.id, role="user", content=text))
        db.commit()
        return agent, conv.id, list(conv.api_messages or [])


def _close_turn(conv_id: int, messages: list[dict] | None, sensitive: bool, answer: str, sources: list[dict],
                trace: list[dict]) -> int:
    """Persist the assistant answer; history only when the run ended consistently (blocking: run in a thread)."""
    with SessionLocal() as db:
        conv = db.get(Conversation, conv_id)
        if messages is not None:
            conv.api_messages = messages  # append-only history, committed only when consistent
        if sensitive:
            conv.sensitive = True
        conv.updated_at = utcnow()
        msg = ChatMessage(conversation_id=conv_id, role="assistant", content=answer, sources=sources, trace=trace)
        db.add(msg)
        db.commit()
        return msg.id


async def chat_turn(p: Principal, text: str, conversation_id: int | None = None,
                    agent_id: str | None = None) -> AsyncIterator[dict]:
    platform = get_platform()
    agent, conv_id, history = await asyncio.to_thread(_open_turn, p, text, conversation_id, agent_id)

    yield {"type": "conversation", "conversation_id": conv_id, "agent_id": agent.id}

    messages = [*history, {"role": "user", "content": text}]
    ctx = ToolContext(user=p, platform=platform, agent=agent, conversation_id=conv_id)
    answer_parts: list[str] = []
    trace: list[dict] = []
    status, end_text = "error", ""

    async for ev in runtime.run(agent, messages, ctx, depth=0):
        if ev["type"] == "text" and ev["depth"] == 0:
            answer_parts.append(ev["text"])
        if ev["type"] in TRACE_EVENTS:
            trace.append({k: v for k, v in ev.items() if k != "type"} | {"event": ev["type"]})
        if ev["type"] == "agent_end" and ev["depth"] == 0:
            status, end_text = ev["status"], ev["text"]
        yield ev

    answer = "".join(answer_parts).strip()
    if status != "ok":
        answer = (answer + "\n\n" if answer else "") + f"⚠️ {end_text}"
    used = {int(n) for n in re.findall(r"\[(\d+)\]", answer)}
    sources = [{k: s[k] for k in ("n", "doc_title", "kb_id", "kb_name", "heading", "text", "classification")}
               for s in ctx.sources if s["n"] in used]

    msg_id = await asyncio.to_thread(_close_turn, conv_id, messages if status == "ok" else None,
                                     bool(ctx.sensitive), answer, sources, trace)

    yield {"type": "done", "message_id": msg_id, "status": status, "content": answer, "sources": sources,
           "sensitive": bool(ctx.sensitive),
           "approvals": [{k: v for k, v in a.items() if not k.startswith("_")} for a in ctx.approvals]}


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
