"""Knowledge bases: list / upload / delete documents, ACL-filtered search."""
from __future__ import annotations

import asyncio

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from pydantic import BaseModel
from sqlalchemy import select

from app.access import Principal
from app.access.auth import current_principal
from app.agents.registry import get_platform
from app.core.db import SessionLocal
from app.models import Document
from app.rag import knowledge
from app.rag.service import acl_allows

router = APIRouter(tags=["knowledge"])
MAX_UPLOAD_BYTES = 20 * 1024 * 1024
CLASSIFICATIONS = ("internal", "confidential", "restricted")


class SearchIn(BaseModel):
    query: str
    kb_ids: list[str] | None = None
    top_k: int = 5


@router.get("/kbs/{kb_id}/documents")
def list_documents(kb_id: str, p: Principal = Depends(current_principal)):
    platform = get_platform()
    if kb_id not in {k.id for k in platform.kbs_for(p)}:
        raise HTTPException(403, "Không có quyền")
    manager = platform.can_manage_kb(kb_id, p)
    with SessionLocal() as db:
        docs = db.scalars(select(Document).where(Document.kb_id == kb_id).order_by(Document.created_at.desc())).all()
    # Documents the user cannot read are invisible (not even their titles), except to KB managers.
    return [{"id": d.id, "title": d.title, "filename": d.filename, "num_chunks": d.num_chunks,
             "classification": d.classification, "acl": d.acl, "created_at": d.created_at}
            for d in docs if manager or acl_allows(d.acl, p)]


@router.post("/kbs/{kb_id}/documents")
async def upload_document(kb_id: str, file: UploadFile = File(...), title: str | None = Form(None),
                          classification: str = Form("internal"), roles: str | None = Form(None),
                          min_level: int | None = Form(None), p: Principal = Depends(current_principal)):
    if not get_platform().can_manage_kb(kb_id, p):
        raise HTTPException(403, "Bạn không có quyền quản lý knowledge base này")
    if classification not in CLASSIFICATIONS:
        raise HTTPException(400, "classification không hợp lệ")
    data = await file.read(MAX_UPLOAD_BYTES + 1)
    if len(data) > MAX_UPLOAD_BYTES:
        raise HTTPException(413, "File quá lớn (tối đa 20MB)")
    acl: dict = {}
    if roles:
        acl["roles"] = [r.strip() for r in roles.split(",") if r.strip()]
    if min_level:
        acl["min_level"] = min_level
    try:
        doc = await asyncio.to_thread(knowledge.ingest, kb_id, file.filename or "document.txt", data, title or None,
                                      p.user_id, classification, acl)
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc
    return {"id": doc.id, "title": doc.title, "num_chunks": doc.num_chunks}


@router.delete("/documents/{doc_id}")
def delete_document(doc_id: int, p: Principal = Depends(current_principal)):
    with SessionLocal() as db:
        doc = db.get(Document, doc_id)
    if doc is None:
        raise HTTPException(404, "Không tìm thấy")
    if not get_platform().can_manage_kb(doc.kb_id, p):
        raise HTTPException(403, "Không có quyền")
    knowledge.delete_document(doc_id)
    return {"ok": True}


@router.post("/kbs/search")
def search(body: SearchIn, p: Principal = Depends(current_principal)):
    allowed = [k.id for k in get_platform().kbs_for(p)]
    kb_ids = [k for k in (body.kb_ids or allowed) if k in allowed]
    return knowledge.search(body.query, kb_ids, max(1, min(body.top_k, 20)), principal=p)
