from __future__ import annotations

from datetime import datetime, time, timedelta
from zoneinfo import ZoneInfo

from pydantic import BaseModel

from src.config import settings
from src.google_client import freebusy_query


class SlotSuggestion(BaseModel):
    start: str
    end: str
    attendees_free: int
    attendees_total: int
    confidence: float


def _parse_hhmm(value: str) -> time:
    hour, minute = value.split(":")
    return time(int(hour), int(minute))


def _candidate_starts(days_ahead: int, duration_minutes: int, tz: ZoneInfo) -> list[datetime]:
    work_start = _parse_hhmm(settings.working_hours_start)
    work_end = _parse_hhmm(settings.working_hours_end)
    granularity = timedelta(minutes=settings.slot_granularity_minutes)
    duration = timedelta(minutes=duration_minutes)

    today = datetime.now(tz).date()
    candidates: list[datetime] = []

    for offset in range(1, days_ahead + 1):
        day = today + timedelta(days=offset)
        if day.weekday() >= 5:
            continue
        if day.isoformat() in settings.india_public_holidays:
            continue

        cursor = datetime.combine(day, work_start, tzinfo=tz)
        day_end = datetime.combine(day, work_end, tzinfo=tz)

        while cursor + duration <= day_end:
            candidates.append(cursor)
            cursor += granularity

    return candidates


def _is_free(slot_start: datetime, slot_end: datetime, busy: list[tuple[datetime, datetime]]) -> bool:
    return all(slot_end <= b_start or slot_start >= b_end for b_start, b_end in busy)


async def find_slots(
    attendees: list[str],
    duration_minutes: int = 30,
    days_ahead: int = 7,
    top_n: int = 3,
) -> list[SlotSuggestion]:
    if not attendees:
        raise ValueError("at least one attendee is required")

    tz = ZoneInfo(settings.calendar_timezone)
    time_min = datetime.now(tz)
    time_max = time_min + timedelta(days=days_ahead + 1)

    busy_by_attendee = await freebusy_query(attendees, time_min, time_max)
    candidates = _candidate_starts(days_ahead, duration_minutes, tz)

    scored: list[SlotSuggestion] = []
    for start in candidates:
        end = start + timedelta(minutes=duration_minutes)
        free_count = sum(
            1 for attendee in attendees if _is_free(start, end, busy_by_attendee.get(attendee, []))
        )
        if free_count == 0:
            continue
        scored.append(
            SlotSuggestion(
                start=start.isoformat(),
                end=end.isoformat(),
                attendees_free=free_count,
                attendees_total=len(attendees),
                confidence=round(free_count / len(attendees), 2),
            )
        )

    scored.sort(key=lambda s: (-s.confidence, s.start))
    return scored[:top_n]
