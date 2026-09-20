from __future__ import annotations

from typing import Any

from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client
from mcp.types import TextContent

from src.core.config import settings


class McpToolError(RuntimeError):
    pass


def _error_message(result: Any) -> str:
    if result.content and isinstance(result.content[0], TextContent):
        return result.content[0].text
    return "unknown MCP tool error"


async def _call_tool(name: str, arguments: dict[str, Any]) -> dict[str, Any]:
    async with (
        streamable_http_client(settings.mcp_calendar_url) as (read, write),
        ClientSession(read, write) as session,
    ):
        await session.initialize()
        result = await session.call_tool(name, arguments)
        if result.is_error:
            raise McpToolError(f"{name} failed: {_error_message(result)}")
        structured: dict[str, Any] = result.structured_content or {}
        return structured


async def find_slots(
    attendees: list[str], duration_minutes: int = 30, days_ahead: int = 7
) -> list[dict[str, Any]]:
    structured = await _call_tool(
        "find_slots",
        {"attendees": attendees, "duration_minutes": duration_minutes, "days_ahead": days_ahead},
    )
    result: list[dict[str, Any]] = structured["result"]
    return result


async def create_event(
    organizer_calendar_id: str,
    summary: str,
    description: str,
    start: str,
    end: str,
    attendees: list[str],
) -> dict[str, Any]:
    structured = await _call_tool(
        "create_event",
        {
            "organizer_calendar_id": organizer_calendar_id,
            "summary": summary,
            "description": description,
            "start": start,
            "end": end,
            "attendees": attendees,
        },
    )
    return structured
