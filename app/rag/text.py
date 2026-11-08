"""Chunking and Vietnamese-aware tokenization."""
from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass

_HEADING = re.compile(r"^(#{1,6})\s+(.*)$")
_WORD = re.compile(r"\w+", re.UNICODE)


def strip_accents(text: str) -> str:
    text = text.replace("đ", "d").replace("Đ", "D")
    nfd = unicodedata.normalize("NFD", text)
    return "".join(ch for ch in nfd if unicodedata.category(ch) != "Mn")


def tokenize(text: str) -> list[str]:
    """Tokens = syllables (with and without diacritics) + accent-free syllable bigrams.

    Vietnamese words are often two syllables ("nghỉ phép"), so bigrams sharpen matching,
    and accent-free forms let queries typed without diacritics still match.
    """
    text = unicodedata.normalize("NFC", text.lower())
    words = _WORD.findall(text)
    plain = [strip_accents(w) for w in words]
    tokens = list(words)
    tokens += [p for w, p in zip(words, plain) if p != w]
    tokens += [f"{a}_{b}" for a, b in zip(plain, plain[1:])]
    return tokens


@dataclass
class TextChunk:
    heading: str
    text: str


def chunk_markdown(text: str, size: int = 900, overlap: int = 150) -> list[TextChunk]:
    """Split by headings, then pack paragraphs up to `size` chars with `overlap`."""
    sections: list[tuple[str, list[str]]] = []
    path: list[str] = []
    current: list[str] = []

    def flush():
        if any(p.strip() for p in current):
            sections.append((" > ".join(path), current.copy()))
        current.clear()

    for para in re.split(r"\n\s*\n", text.replace("\r\n", "\n")):
        para = para.strip()
        if not para:
            continue
        m = _HEADING.match(para.splitlines()[0])
        if m:
            flush()
            level = len(m.group(1))
            path[:] = path[: level - 1] + [m.group(2).strip()]
            rest = "\n".join(para.splitlines()[1:]).strip()
            if rest:
                current.append(rest)
        else:
            current.append(para)
    flush()

    chunks: list[TextChunk] = []
    for heading, paras in sections:
        buf = ""
        for para in paras:
            while len(para) > size:  # hard-split very long paragraphs
                head, para = para[:size], para[size - overlap:]
                if buf:
                    chunks.append(TextChunk(heading, buf))
                    buf = ""
                chunks.append(TextChunk(heading, head))
            if buf and len(buf) + len(para) + 2 > size:
                chunks.append(TextChunk(heading, buf))
                tail = buf[-overlap:] if overlap else ""
                # start the overlap at a word boundary
                tail = tail[tail.find(" ") + 1:] if " " in tail else tail
                buf = f"{tail}\n\n{para}" if tail else para
            else:
                buf = f"{buf}\n\n{para}" if buf else para
        if buf:
            chunks.append(TextChunk(heading, buf))
    return chunks
