from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel

from src.google_client import insert_event


class EventResult(BaseModel):
    event_id: str
    html_link: str
    status: str


async def create_event(
    organizer_calendar_id: str,
    summary: str,
    description: str,
    start: str,
    end: str,
    attendees: list[str],
) -> EventResult:
    created = await insert_event(
        calendar_id=organizer_calendar_id,
        summary=summary,
        description=description,
        start=datetime.fromisoformat(start),
        end=datetime.fromisoformat(end),
        attendees=attendees,
    )
    return EventResult(
        event_id=created["id"],
        html_link=created.get("htmlLink", ""),
        status=created.get("status", "unknown"),
    )
