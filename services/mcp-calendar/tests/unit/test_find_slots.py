from __future__ import annotations

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import pytest

from src.tools import find_slots as find_slots_module


@pytest.mark.asyncio
async def test_find_slots_prefers_fully_free_attendees(monkeypatch: pytest.MonkeyPatch) -> None:
    async def fake_freebusy_query(calendar_ids: list[str], time_min: datetime, time_max: datetime) -> dict:
        return {"a@example.com": [], "b@example.com": []}

    monkeypatch.setattr(find_slots_module, "freebusy_query", fake_freebusy_query)

    suggestions = await find_slots_module.find_slots(
        attendees=["a@example.com", "b@example.com"],
        duration_minutes=30,
        days_ahead=7,
        top_n=3,
    )

    assert len(suggestions) == 3
    assert all(s.confidence == 1.0 for s in suggestions)
    assert all(s.attendees_free == 2 for s in suggestions)


@pytest.mark.asyncio
async def test_find_slots_ranks_partial_availability_lower(monkeypatch: pytest.MonkeyPatch) -> None:
    async def fake_freebusy_query(calendar_ids: list[str], time_min: datetime, time_max: datetime) -> dict:
        tz = ZoneInfo("Asia/Kolkata")
        far_future = datetime.now(tz) + timedelta(days=30)
        return {
            "a@example.com": [],
            "b@example.com": [(datetime.now(tz), far_future)],
        }

    monkeypatch.setattr(find_slots_module, "freebusy_query", fake_freebusy_query)

    suggestions = await find_slots_module.find_slots(
        attendees=["a@example.com", "b@example.com"],
        duration_minutes=30,
        days_ahead=7,
        top_n=3,
    )

    assert len(suggestions) == 3
    assert all(s.confidence == 0.5 for s in suggestions)
    assert all(s.attendees_free == 1 for s in suggestions)


@pytest.mark.asyncio
async def test_find_slots_excludes_weekends(monkeypatch: pytest.MonkeyPatch) -> None:
    async def fake_freebusy_query(calendar_ids: list[str], time_min: datetime, time_max: datetime) -> dict:
        return {"a@example.com": []}

    monkeypatch.setattr(find_slots_module, "freebusy_query", fake_freebusy_query)

    suggestions = await find_slots_module.find_slots(
        attendees=["a@example.com"],
        duration_minutes=30,
        days_ahead=7,
        top_n=100,
    )

    assert suggestions
    for s in suggestions:
        assert datetime.fromisoformat(s.start).weekday() < 5


@pytest.mark.asyncio
async def test_find_slots_excludes_public_holidays(monkeypatch: pytest.MonkeyPatch) -> None:
    tz = ZoneInfo("Asia/Kolkata")
    holiday = datetime.now(tz).date() + timedelta(days=1)
    while holiday.weekday() >= 5:
        holiday += timedelta(days=1)

    monkeypatch.setattr(find_slots_module.settings, "india_public_holidays", [holiday.isoformat()])

    async def fake_freebusy_query(calendar_ids: list[str], time_min: datetime, time_max: datetime) -> dict:
        return {"a@example.com": []}

    monkeypatch.setattr(find_slots_module, "freebusy_query", fake_freebusy_query)

    suggestions = await find_slots_module.find_slots(
        attendees=["a@example.com"],
        duration_minutes=30,
        days_ahead=7,
        top_n=100,
    )

    assert suggestions
    for s in suggestions:
        assert datetime.fromisoformat(s.start).date() != holiday


@pytest.mark.asyncio
async def test_find_slots_requires_attendees() -> None:
    with pytest.raises(ValueError):
        await find_slots_module.find_slots(attendees=[])
