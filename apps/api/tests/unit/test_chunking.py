from __future__ import annotations

from src.services.chunking import chunk_meeting_minutes


def test_chunk_meeting_minutes_splits_on_agenda_items() -> None:
    text = """Agenda Item 1: Budget review
Discussed Q2 budget overrun in the roads department.

Agenda Item 2: Staffing
Decided to hire 3 new junior engineers."""

    chunks = chunk_meeting_minutes(text)

    assert len(chunks) == 2
    assert chunks[0].startswith("Agenda Item 1: Budget review")
    assert chunks[1].startswith("Agenda Item 2: Staffing")


def test_chunk_meeting_minutes_no_agenda_markers_returns_whole_text() -> None:
    text = "Just some free-form notes with no agenda item headings."

    chunks = chunk_meeting_minutes(text)

    assert chunks == [text]


def test_chunk_meeting_minutes_empty_text_returns_empty_list() -> None:
    assert chunk_meeting_minutes("") == []
    assert chunk_meeting_minutes("   ") == []
