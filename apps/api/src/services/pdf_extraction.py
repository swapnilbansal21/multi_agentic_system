from __future__ import annotations

from pathlib import Path

from pypdf import PdfReader


def extract_text_from_pdf(path: str | Path) -> str:
    reader = PdfReader(str(path))
    pages_text = [page.extract_text() or "" for page in reader.pages]
    return "\n\n".join(pages_text).strip()
