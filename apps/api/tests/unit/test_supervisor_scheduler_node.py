from __future__ import annotations

from typing import Any

import pytest
from sqlalchemy import delete

from src.agents import scheduler as scheduler_module
from src.agents.supervisor import IntentClassification, scheduler_node
from src.db.session import async_session_factory
from src.models.officer import Officer

TEST_EMAIL = "priya.sharma@test.example"


async def _cleanup() -> None:
    async with async_session_factory() as session:
        await session.execute(delete(Officer).where(Officer.email == TEST_EMAIL))
        await session.commit()


@pytest.mark.asyncio
async def test_scheduler_node_resolves_names_to_emails_before_find_slots(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async with async_session_factory() as session:
        session.add(Officer(name="Priya Sharma", email=TEST_EMAIL))
        await session.commit()

    captured: dict[str, Any] = {}

    async def fake_find_slots(
        attendees: list[str], duration_minutes: int, days_ahead: int
    ) -> list[dict[str, Any]]:
        captured["attendees"] = attendees
        return []

    monkeypatch.setattr(scheduler_module, "find_slots", fake_find_slots)

    try:
        state = {
            "query": "schedule with Priya",
            "classification": IntentClassification(
                intent="schedule", attendees=["Priya"], topic="review"
            ),
            "result": None,
        }
        result_state = await scheduler_node(state)  # type: ignore[arg-type]

        assert captured["attendees"] == [TEST_EMAIL]
        assert result_state["result"]["attendees"] == [TEST_EMAIL]
    finally:
        await _cleanup()
