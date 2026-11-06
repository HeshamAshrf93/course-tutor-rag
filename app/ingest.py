"""Reads a PDF page by page and splits it into overlapping, citable chunks."""
import re
from dataclasses import dataclass
from pathlib import Path

from pypdf import PdfReader


@dataclass(frozen=True)
class Chunk:
    id: int
    source: str
    page: int
    heading: str
    text: str


def _split_sentences(text: str) -> list[str]:
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+", " ".join(text.split())) if s.strip()]


def chunk_page(text: str, max_words: int = 70, overlap_sentences: int = 1) -> tuple[str, list[str]]:
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    if not lines:
        return "", []
    heading = lines[0] if len(lines[0].split()) <= 10 else ""
    body = " ".join(lines[1:] if heading else lines)
    sentences, chunks, current = _split_sentences(body), [], []
    for sentence in sentences:
        if current and sum(len(s.split()) for s in current) + len(sentence.split()) > max_words:
            chunks.append(" ".join(current))
            current = current[-overlap_sentences:] if overlap_sentences else []
        current.append(sentence)
    if current:
        chunks.append(" ".join(current))
    return heading, chunks


def load_pdf(path: str | Path) -> list[Chunk]:
    path = Path(path)
    reader = PdfReader(str(path))
    if reader.is_encrypted:
        raise ValueError(f"{path.name} is encrypted")
    out: list[Chunk] = []
    for page_no, page in enumerate(reader.pages, start=1):
        heading, pieces = chunk_page(page.extract_text() or "")
        for piece in pieces:
            out.append(Chunk(len(out), path.name, page_no, heading, piece))
    if not out:
        raise ValueError(f"No extractable text in {path.name}; scanned PDFs need OCR first")
    return out
