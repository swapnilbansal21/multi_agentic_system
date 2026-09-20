from __future__ import annotations

from typing import Any

from mcp.server.mcpserver import MCPServer

from src.config import settings
from src.tools.create_event import create_event as _create_event
from src.tools.find_slots import find_slots as _find_slots

mcp = MCPServer("mcp-calendar")


@mcp.tool()
async def find_slots(
    attendees: list[str], duration_minutes: int = 30, days_ahead: int = 7
) -> list[dict[str, Any]]:
    """Read-only. Returns up to 3 free slots across all attendees' Google Calendars,
    ranked by how many attendees are free, respecting working hours and India public holidays."""
    suggestions = await _find_slots(attendees, duration_minutes, days_ahead)
    return [s.model_dump() for s in suggestions]


@mcp.tool()
async def create_event(
    organizer_calendar_id: str,
    summary: str,
    description: str,
    start: str,
    end: str,
    attendees: list[str],
) -> dict[str, Any]:
    """WRITE tool — sends real Google Calendar invites to all attendees.
    Per FR-19, this must only be invoked after explicit human approval at the API layer.
    Agents must never call this autonomously from reasoning alone."""
    result = await _create_event(organizer_calendar_id, summary, description, start, end, attendees)
    return result.model_dump()


if __name__ == "__main__":
    mcp.run(transport="streamable-http", host=settings.host, port=settings.port, stateless_http=True)
