from __future__ import annotations

from typing import Any

import pytest

from src.tools import create_event as create_event_module


@pytest.mark.asyncio
async def test_create_event_maps_google_response(monkeypatch: pytest.MonkeyPatch) -> None:
    async def fake_insert_event(
        calendar_id: str,
        summary: str,
        description: str,
        start: Any,
        end: Any,
        attendees: list[str],
    ) -> dict[str, Any]:
        assert calendar_id == "organizer@example.com"
        assert attendees == ["a@example.com", "b@example.com"]
        return {"id": "evt_123", "htmlLink": "https://calendar.google.com/evt_123", "status": "confirmed"}

    monkeypatch.setattr(create_event_module, "insert_event", fake_insert_event)

    result = await create_event_module.create_event(
        organizer_calendar_id="organizer@example.com",
        summary="Review meeting",
        description="Quarterly review",
        start="2026-10-01T10:00:00+05:30",
        end="2026-10-01T10:30:00+05:30",
        attendees=["a@example.com", "b@example.com"],
    )

    assert result.event_id == "evt_123"
    assert result.html_link == "https://calendar.google.com/evt_123"
    assert result.status == "confirmed"


@pytest.mark.asyncio
async def test_create_event_defaults_missing_fields(monkeypatch: pytest.MonkeyPatch) -> None:
    async def fake_insert_event(
        calendar_id: str,
        summary: str,
        description: str,
        start: Any,
        end: Any,
        attendees: list[str],
    ) -> dict[str, Any]:
        return {"id": "evt_456"}

    monkeypatch.setattr(create_event_module, "insert_event", fake_insert_event)

    result = await create_event_module.create_event(
        organizer_calendar_id="organizer@example.com",
        summary="No-frills meeting",
        description="",
        start="2026-10-01T10:00:00+05:30",
        end="2026-10-01T10:30:00+05:30",
        attendees=[],
    )

    assert result.event_id == "evt_456"
    assert result.html_link == ""
    assert result.status == "unknown"
