from __future__ import annotations

from typing import Any

import pytest

from src.agents import scheduler as scheduler_module
from src.routers import agents as agents_module
from src.routers.agents import ScheduleSuggestRequest, suggest_meeting_slots


@pytest.mark.asyncio
async def test_run_scheduler_agent_forwards_duration_and_days_ahead(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, Any] = {}

    async def fake_find_slots(
        attendees: list[str], duration_minutes: int, days_ahead: int
    ) -> list[dict[str, Any]]:
        captured["attendees"] = attendees
        captured["duration_minutes"] = duration_minutes
        captured["days_ahead"] = days_ahead
        return [{"start": "2026-09-22T15:00:00+05:30", "end": "2026-09-22T15:30:00+05:30"}]

    monkeypatch.setattr(scheduler_module, "find_slots", fake_find_slots)

    result = await scheduler_module.run_scheduler_agent(
        {"attendees": ["a@example.com"], "duration_minutes": 60, "days_ahead": 3}
    )

    assert captured == {"attendees": ["a@example.com"], "duration_minutes": 60, "days_ahead": 3}
    assert result["agent"] == "scheduler"
    assert result["suggested_slots"] == [
        {"start": "2026-09-22T15:00:00+05:30", "end": "2026-09-22T15:30:00+05:30"}
    ]


@pytest.mark.asyncio
async def test_run_scheduler_agent_defaults_duration_and_days_ahead(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, Any] = {}

    async def fake_find_slots(
        attendees: list[str], duration_minutes: int, days_ahead: int
    ) -> list[dict[str, Any]]:
        captured["duration_minutes"] = duration_minutes
        captured["days_ahead"] = days_ahead
        return []

    monkeypatch.setattr(scheduler_module, "find_slots", fake_find_slots)

    await scheduler_module.run_scheduler_agent({"attendees": ["a@example.com"]})

    assert captured == {"duration_minutes": 30, "days_ahead": 7}


@pytest.mark.asyncio
async def test_suggest_meeting_slots_endpoint_bypasses_supervisor(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def fake_run_scheduler_agent(payload: dict[str, Any]) -> dict[str, Any]:
        return {"agent": "scheduler", "suggested_slots": [], "attendees": payload["attendees"]}

    monkeypatch.setattr(agents_module, "run_scheduler_agent", fake_run_scheduler_agent)

    request = ScheduleSuggestRequest(attendees=["a@example.com", "b@example.com"])
    result = await suggest_meeting_slots(request)

    assert result["attendees"] == ["a@example.com", "b@example.com"]
