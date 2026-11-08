"""Conversation service: one user turn → orchestrated agent run → persisted result."""
from __future__ import annotations

import re
from typing import AsyncIterator

from .db import ChatMessage, Conversation, SessionLocal, utcnow
from .orchestrator import runtime
from .policy import Principal
from .registry import get_platform
from .tools import ToolContext

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


async def chat_turn(p: Principal, text: str, conversation_id: int | None = None,
                    agent_id: str | None = None) -> AsyncIterator[dict]:
    platform = get_platform()
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
        conv_id, history = conv.id, list(conv.api_messages or [])

    yield {"type": "conversation", "conversation_id": conv_id, "agent_id": agent.id}

    messages = history + [{"role": "user", "content": text}]
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

    with SessionLocal() as db:
        conv = db.get(Conversation, conv_id)
        if status == "ok":
            conv.api_messages = messages  # append-only history, committed only when consistent
        if ctx.sensitive:
            conv.sensitive = True
        conv.updated_at = utcnow()
        msg = ChatMessage(conversation_id=conv_id, role="assistant", content=answer, sources=sources, trace=trace)
        db.add(msg)
        db.commit()
        msg_id = msg.id

    yield {"type": "done", "message_id": msg_id, "status": status, "content": answer, "sources": sources,
           "sensitive": bool(ctx.sensitive),
           "approvals": [{k: v for k, v in a.items() if not k.startswith("_")} for a in ctx.approvals]}
