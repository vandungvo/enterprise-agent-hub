"""Knowledge-base ingestion and hybrid retrieval (BM25 + optional embeddings, fused by RRF)."""
from __future__ import annotations

import math
import threading
from collections import Counter
from dataclasses import dataclass

import numpy as np
from sqlalchemy import delete, select

from ..db import Chunk, Document, SessionLocal
from ..settings import settings
from .parsing import extract_text
from .text import chunk_markdown, tokenize


# --------------------------------------------------------------------------- embeddings
class Embedder:
    """Optional dense embeddings. Enable with RAG_EMBEDDINGS=fastembed (pip install fastembed)."""

    def __init__(self) -> None:
        self._model = None
        self.enabled = settings.embeddings == "fastembed"

    def _load(self):
        if self._model is None:
            from fastembed import TextEmbedding  # optional dependency

            self._model = TextEmbedding(settings.embedding_model)
        return self._model

    def embed(self, texts: list[str]) -> np.ndarray:
        vecs = np.array(list(self._load().embed(texts)), dtype=np.float32)
        norms = np.linalg.norm(vecs, axis=1, keepdims=True)
        return vecs / np.clip(norms, 1e-9, None)


embedder = Embedder()


# --------------------------------------------------------------------------- BM25 index
@dataclass
class _Entry:
    chunk_id: int
    kb_id: str
    doc_id: int
    doc_title: str
    heading: str
    text: str
    classification: str
    acl: dict
    tf: Counter
    length: int
    vector: np.ndarray | None


class _Index:
    k1, b = 1.5, 0.75

    def __init__(self) -> None:
        self.entries: list[_Entry] = []
        self.df: Counter = Counter()
        self.avgdl = 1.0
        self.matrix: np.ndarray | None = None

    @classmethod
    def build(cls) -> "_Index":
        idx = cls()
        with SessionLocal() as db:
            rows = db.execute(
                select(Chunk, Document.title, Document.classification, Document.acl)
                .join(Document, Chunk.document_id == Document.id)
            ).all()
        for chunk, title, classification, acl in rows:
            toks = tokenize(f"{title} {chunk.heading} {chunk.text}")
            vec = np.frombuffer(chunk.embedding, dtype=np.float32) if chunk.embedding else None
            idx.entries.append(_Entry(chunk.id, chunk.kb_id, chunk.document_id, title, chunk.heading,
                                      chunk.text, classification or "internal", acl or {}, Counter(toks),
                                      len(toks), vec))
        for e in idx.entries:
            idx.df.update(e.tf.keys())
        if idx.entries:
            idx.avgdl = sum(e.length for e in idx.entries) / len(idx.entries)
            if embedder.enabled and all(e.vector is not None for e in idx.entries):
                idx.matrix = np.vstack([e.vector for e in idx.entries])
        return idx

    def bm25(self, query: str, allowed: set[int]) -> list[tuple[int, float]]:
        n = len(self.entries)
        q = set(tokenize(query))
        scores = []
        for i in allowed:
            e = self.entries[i]
            s = 0.0
            for t in q:
                f = e.tf.get(t)
                if not f:
                    continue
                idf = math.log(1 + (n - self.df[t] + 0.5) / (self.df[t] + 0.5))
                s += idf * f * (self.k1 + 1) / (f + self.k1 * (1 - self.b + self.b * e.length / self.avgdl))
            if s > 0:
                scores.append((i, s))
        return sorted(scores, key=lambda x: -x[1])

    def dense(self, query: str, allowed: set[int]) -> list[tuple[int, float]]:
        if self.matrix is None or not allowed:
            return []
        qv = embedder.embed([query])[0]
        ids = np.array(sorted(allowed))
        sims = self.matrix[ids] @ qv
        order = np.argsort(-sims)
        return [(int(ids[j]), float(sims[j])) for j in order[:50]]


def acl_allows(acl: dict, p) -> bool:
    """Document ACL: all present conditions must hold (roles = any-of, units = within any subtree)."""
    if not acl:
        return True
    if acl.get("roles") and not (set(acl["roles"]) & p.roles):
        return False
    if acl.get("min_level") and p.level < acl["min_level"]:
        return False
    if acl.get("units"):
        ancestors = set(p.org.ancestors(p.unit_code))
        if not ancestors & set(acl["units"]):
            return False
    return True


class KnowledgeService:
    def __init__(self) -> None:
        self._index: _Index | None = None
        self._lock = threading.Lock()

    # ---- index lifecycle ---------------------------------------------------
    def invalidate(self) -> None:
        with self._lock:
            self._index = None

    def _get_index(self) -> _Index:
        with self._lock:
            if self._index is None:
                self._index = _Index.build()
            return self._index

    # ---- ingestion -----------------------------------------------------------
    def ingest(self, kb_id: str, filename: str, data: bytes, title: str | None = None,
               uploaded_by: int | None = None, classification: str = "internal",
               acl: dict | None = None) -> Document:
        text = extract_text(filename, data)
        if not text.strip():
            raise ValueError("Không trích xuất được nội dung văn bản từ file")
        pieces = chunk_markdown(text, settings.chunk_size, settings.chunk_overlap)
        vectors = embedder.embed([f"{p.heading}\n{p.text}" for p in pieces]) if embedder.enabled else None
        with SessionLocal() as db:
            doc = Document(kb_id=kb_id, title=title or filename.rsplit(".", 1)[0], filename=filename,
                           uploaded_by=uploaded_by, num_chunks=len(pieces), classification=classification,
                           acl=acl or {})
            db.add(doc)
            db.flush()
            for i, p in enumerate(pieces):
                db.add(Chunk(document_id=doc.id, kb_id=kb_id, ordinal=i, heading=p.heading, text=p.text,
                             embedding=vectors[i].tobytes() if vectors is not None else None))
            db.commit()
        self.invalidate()
        return doc

    def delete_document(self, doc_id: int) -> None:
        with SessionLocal() as db:
            db.execute(delete(Chunk).where(Chunk.document_id == doc_id))
            db.execute(delete(Document).where(Document.id == doc_id))
            db.commit()
        self.invalidate()

    # ---- retrieval -----------------------------------------------------------
    def search(self, query: str, kb_ids: list[str], top_k: int = 5, principal=None) -> list[dict]:
        """`principal` enforces document-level ACLs; pass it on every user-facing call."""
        idx = self._get_index()
        kb_set = set(kb_ids)
        allowed = {i for i, e in enumerate(idx.entries)
                   if e.kb_id in kb_set and (principal is None or acl_allows(e.acl, principal))}
        if not allowed or not query.strip():
            return []
        lexical = idx.bm25(query, allowed)[:50]
        dense = idx.dense(query, allowed)
        # Reciprocal Rank Fusion
        fused: dict[int, float] = {}
        for ranking in (lexical, dense):
            for rank, (i, _) in enumerate(ranking):
                fused[i] = fused.get(i, 0.0) + 1.0 / (60 + rank)
        best = sorted(fused.items(), key=lambda x: -x[1])[:top_k]
        results = []
        for i, score in best:
            e = idx.entries[i]
            results.append({"chunk_id": e.chunk_id, "doc_id": e.doc_id, "doc_title": e.doc_title,
                            "kb_id": e.kb_id, "heading": e.heading, "text": e.text,
                            "classification": e.classification, "score": round(score, 5)})
        return results


knowledge = KnowledgeService()
