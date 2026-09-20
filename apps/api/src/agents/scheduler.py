from typing import Any

from src.services.mcp_calendar_client import find_slots


async def run_scheduler_agent(payload: dict[str, Any]) -> dict[str, Any]:
    attendees = payload.get("attendees", [])
    suggestions = await find_slots(
        attendees=attendees,
        duration_minutes=payload.get("duration_minutes", 30),
        days_ahead=payload.get("days_ahead", 7),
    )
    return {
        "agent": "scheduler",
        "suggested_slots": suggestions,
        "attendees": attendees,
    }
