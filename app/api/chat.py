"""Chat (SSE streaming), conversation history and answer feedback."""
from __future__ import annotations

import json
import logging

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from sqlalchemy import delete, select

from app.access import Principal
from app.access.auth import current_principal
from app.agents.conversation import ChatError, chat_turn
from app.core.db import SessionLocal
from app.core.observability import current_request_id
from app.models import ChatMessage, Conversation

log = logging.getLogger("agenthub.api.chat")
router = APIRouter(tags=["chat"])
MAX_MESSAGE_CHARS = 8000


class ChatIn(BaseModel):
    message: str = Field(max_length=MAX_MESSAGE_CHARS)
    conversation_id: int | None = None
    agent_id: str | None = None


class FeedbackIn(BaseModel):
    value: int
    comment: str | None = Field(default=None, max_length=2000)


def _sse(event: dict) -> str:
    return f"data: {json.dumps(event, ensure_ascii=False, default=str)}\n\n"


@router.post("/chat")
async def chat(body: ChatIn, p: Principal = Depends(current_principal)):
    if not body.message.strip():
        raise HTTPException(400, "Tin nhắn trống")

    async def stream():
        try:
            async for ev in chat_turn(p, body.message, body.conversation_id, body.agent_id):
                yield _sse(ev)
        except ChatError as exc:
            yield _sse({"type": "error", "text": str(exc)})
        except Exception:  # keep the stream well-formed; details go to the log, not the client
            log.exception("chat failed")
            yield _sse({"type": "error", "text": f"Lỗi hệ thống, vui lòng thử lại (mã lỗi: {current_request_id()})."})

    return StreamingResponse(stream(), media_type="text/event-stream",
                             headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})


def _own_conversation(db, conv_id: int, p: Principal) -> Conversation:
    conv = db.get(Conversation, conv_id)
    if conv is None or conv.user_id != p.user_id:
        raise HTTPException(404, "Không tìm thấy")
    return conv


@router.get("/conversations")
def list_conversations(p: Principal = Depends(current_principal)):
    with SessionLocal() as db:
        rows = db.scalars(select(Conversation).where(Conversation.user_id == p.user_id)
                          .order_by(Conversation.updated_at.desc(), Conversation.id.desc()).limit(100)).all()
    return [{"id": c.id, "title": c.title, "agent_id": c.agent_id, "sensitive": c.sensitive,
             "updated_at": c.updated_at} for c in rows]


@router.get("/conversations/{conv_id}")
def get_conversation(conv_id: int, p: Principal = Depends(current_principal)):
    with SessionLocal() as db:
        conv = _own_conversation(db, conv_id, p)
        msgs = db.scalars(select(ChatMessage).where(ChatMessage.conversation_id == conv_id)
                          .order_by(ChatMessage.id)).all()
    return {"id": conv.id, "title": conv.title, "agent_id": conv.agent_id, "sensitive": conv.sensitive,
            "messages": [{"id": m.id, "role": m.role, "content": m.content, "sources": m.sources,
                          "trace": m.trace, "feedback": m.feedback} for m in msgs]}


@router.delete("/conversations/{conv_id}")
def delete_conversation(conv_id: int, p: Principal = Depends(current_principal)):
    with SessionLocal() as db:
        conv = _own_conversation(db, conv_id, p)
        db.execute(delete(ChatMessage).where(ChatMessage.conversation_id == conv_id))
        db.delete(conv)
        db.commit()
    return {"ok": True}


@router.post("/messages/{msg_id}/feedback")
def feedback(msg_id: int, body: FeedbackIn, p: Principal = Depends(current_principal)):
    with SessionLocal() as db:
        msg = db.get(ChatMessage, msg_id)
        if msg is None:
            raise HTTPException(404, "Không tìm thấy")
        _own_conversation(db, msg.conversation_id, p)
        msg.feedback = 1 if body.value > 0 else -1
        msg.feedback_comment = body.comment
        db.commit()
    return {"ok": True}
