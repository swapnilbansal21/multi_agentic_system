from typing import Any

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from src.agents.scheduler import run_scheduler_agent
from src.agents.supervisor import run_supervisor
from src.core.auth import CurrentOfficer, get_current_officer, require_role
from src.services.mcp_calendar_client import create_event

router = APIRouter()


class AgentQueryRequest(BaseModel):
    query: str


@router.post("/agent/query")
async def agent_query(
    request: AgentQueryRequest,
    officer: CurrentOfficer = Depends(get_current_officer),
) -> dict[str, Any]:
    return await run_supervisor(request.query, organizer_email=officer.email)


class ScheduleSuggestRequest(BaseModel):
    attendees: list[str]
    duration_minutes: int = 30
    days_ahead: int = 7


@router.post("/schedule-meeting/suggest")
async def suggest_meeting_slots(
    request: ScheduleSuggestRequest,
    officer: CurrentOfficer = Depends(get_current_officer),
) -> dict[str, Any]:
    """FR-01: deterministic slot lookup for callers that already know the attendee
    list (e.g. a form-based UI) — bypasses the LLM intent classifier in run_supervisor."""
    return await run_scheduler_agent(
        {
            "attendees": request.attendees,
            "duration_minutes": request.duration_minutes,
            "days_ahead": request.days_ahead,
            "organizer_email": officer.email,
        }
    )


class ConfirmMeetingRequest(BaseModel):
    organizer_calendar_id: str
    summary: str
    description: str = ""
    start: str
    end: str
    attendees: list[str]


@router.post("/schedule-meeting/confirm")
async def confirm_meeting(
    request: ConfirmMeetingRequest,
    _officer: CurrentOfficer = Depends(require_role("Admin", "PA")),
) -> dict[str, Any]:
    """FR-19: reachable only by an explicit user action in the app (e.g. tapping
    'Confirm'/'Send'). Never called by agent/supervisor reasoning. Restricted to
    Admin/PA roles since this is the role that actually sends calendar invites."""
    return await create_event(
        organizer_calendar_id=request.organizer_calendar_id,
        summary=request.summary,
        description=request.description,
        start=request.start,
        end=request.end,
        attendees=request.attendees,
    )
