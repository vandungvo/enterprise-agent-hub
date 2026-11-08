"""Extract text from uploaded files."""
from __future__ import annotations

import io
from pathlib import Path

SUPPORTED = {".txt", ".md", ".markdown", ".pdf", ".docx", ".csv"}


def extract_text(filename: str, data: bytes) -> str:
    ext = Path(filename).suffix.lower()
    if ext not in SUPPORTED:
        raise ValueError(f"Định dạng {ext} chưa hỗ trợ. Hỗ trợ: {', '.join(sorted(SUPPORTED))}")
    if ext in {".txt", ".md", ".markdown", ".csv"}:
        for enc in ("utf-8-sig", "utf-16", "cp1258", "latin-1"):
            try:
                return data.decode(enc)
            except UnicodeDecodeError:
                continue
    if ext == ".pdf":
        from pypdf import PdfReader

        reader = PdfReader(io.BytesIO(data))
        pages = []
        for i, page in enumerate(reader.pages, start=1):
            text = (page.extract_text() or "").strip()
            if text:
                pages.append(f"## Trang {i}\n\n{text}")
        return "\n\n".join(pages)
    if ext == ".docx":
        import docx

        doc = docx.Document(io.BytesIO(data))
        lines = []
        for p in doc.paragraphs:
            text = p.text.strip()
            if not text:
                continue
            style = (p.style.name or "").lower() if p.style is not None else ""
            if style.startswith("heading"):
                level = "".join(ch for ch in style if ch.isdigit()) or "2"
                lines.append("#" * min(int(level) + 1, 4) + " " + text)
            else:
                lines.append(text)
        for table in doc.tables:
            for row in table.rows:
                lines.append(" | ".join(c.text.strip() for c in row.cells))
        return "\n\n".join(lines)
    raise ValueError(f"Không đọc được file {filename}")
