from __future__ import annotations

import re

_AGENDA_ITEM_PATTERN = re.compile(r"(?=^Agenda Item \d+:)", re.MULTILINE)


def chunk_meeting_minutes(text: str) -> list[str]:
    """Structural chunking: one chunk per agenda item (per spec §10), not fixed
    token windows — meeting minutes already have this natural boundary."""
    text = text.strip()
    if not text:
        return []

    parts = _AGENDA_ITEM_PATTERN.split(text)
    chunks = [part.strip() for part in parts if part.strip()]
    return chunks if chunks else [text]
