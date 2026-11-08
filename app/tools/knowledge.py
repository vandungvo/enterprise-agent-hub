"""Knowledge search (RAG with document ACLs) and utility tools."""
from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo

from pydantic import Field

from app.rag import knowledge
from app.tools.base import ToolContext, ToolDef, ToolInput, register


class SearchKnowledgeInput(ToolInput):
    query: str = Field(description="Câu truy vấn, dùng từ khóa cụ thể")
    kb_ids: list[str] | None = Field(default=None, description="Giới hạn trong các knowledge base này (bỏ trống = tất cả được phép)")
    top_k: int = Field(default=5, ge=1, le=10)


def _describe_search(ctx: ToolContext) -> str:
    kbs = [ctx.platform.knowledge_bases[k] for k in ctx.allowed_kbs()]
    listing = "\n".join(f"- {k.id}: {k.name} — {k.description}" for k in kbs) or "- (không có)"
    return ("Tìm kiếm tài liệu nội bộ. Trả về đoạn trích kèm số nguồn [n]; khi dùng thông tin hãy trích "
            "dẫn [n]. Kết quả đã được lọc theo quyền đọc tài liệu của người dùng. Có thể gọi nhiều lần.\n"
            f"Knowledge base được phép:\n{listing}")


def _run_search(ctx: ToolContext, inp: SearchKnowledgeInput) -> str:
    allowed = ctx.allowed_kbs()
    kb_ids = [k for k in (inp.kb_ids or allowed) if k in allowed]
    if not kb_ids:
        return "Không có knowledge base nào được phép truy cập cho yêu cầu này."
    hits = knowledge.search(inp.query, kb_ids, inp.top_k, principal=ctx.user)
    if not hits:
        return "Không tìm thấy tài liệu liên quan (trong phạm vi tài liệu người dùng được đọc)."
    out = []
    for h in hits:
        existing = next((s for s in ctx.sources if s["chunk_id"] == h["chunk_id"]), None)
        if existing is None:
            existing = {**h, "n": len(ctx.sources) + 1, "kb_name": ctx.platform.knowledge_bases[h["kb_id"]].name}
            ctx.sources.append(existing)
        loc = h["doc_title"] + (f" › {h['heading']}" if h["heading"] else "")
        label = f" [{h['classification'].upper()}]" if h["classification"] != "internal" else ""
        out.append(f"[{existing['n']}] ({loc}){label}\n{h['text']}")
    return "\n\n---\n\n".join(out)


register(ToolDef(name="search_knowledge", input_model=SearchKnowledgeInput, describe=_describe_search, run=_run_search))


class EmptyInput(ToolInput):
    pass


def _run_time(ctx: ToolContext, _inp: EmptyInput) -> str:
    now = datetime.now(ZoneInfo(ctx.platform.company.get("timezone", "Asia/Ho_Chi_Minh")))
    return now.strftime("%A %Y-%m-%d %H:%M (%Z)")


register(ToolDef(name="get_current_time", input_model=EmptyInput,
                 describe=lambda ctx: "Ngày giờ hiện tại theo múi giờ công ty.", run=_run_time))
