from __future__ import annotations

import asyncio
from datetime import datetime
from pathlib import Path
from typing import Any

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow  # type: ignore[import-untyped]
from googleapiclient.discovery import Resource, build  # type: ignore[import-untyped]

from src.config import settings

SCOPES = ["https://www.googleapis.com/auth/calendar"]

_service: Resource | None = None


def _load_credentials() -> Credentials:
    token_path = Path(settings.google_oauth_token_path)
    creds: Credentials | None = None

    if token_path.exists():
        creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)  # type: ignore[no-untyped-call]

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())  # type: ignore[no-untyped-call]
        else:
            flow = InstalledAppFlow.from_client_secrets_file(settings.google_oauth_credentials_path, SCOPES)
            creds = flow.run_local_server(port=0)
        token_path.write_text(creds.to_json())

    return creds


def _get_service() -> Resource:
    global _service
    if _service is None:
        _service = build("calendar", "v3", credentials=_load_credentials())
    return _service


async def _get_service_async() -> Resource:
    # _get_service() can block for minutes (browser OAuth consent) — run it on a
    # worker thread so it never freezes the server's single asyncio event loop.
    return await asyncio.to_thread(_get_service)


async def freebusy_query(
    calendar_ids: list[str], time_min: datetime, time_max: datetime
) -> dict[str, list[tuple[datetime, datetime]]]:
    service = await _get_service_async()

    def _call() -> dict[str, Any]:
        body = {
            "timeMin": time_min.isoformat(),
            "timeMax": time_max.isoformat(),
            "items": [{"id": cal_id} for cal_id in calendar_ids],
        }
        result: dict[str, Any] = service.freebusy().query(body=body).execute()
        return result

    response = await asyncio.to_thread(_call)

    busy_by_calendar: dict[str, list[tuple[datetime, datetime]]] = {}
    for cal_id, cal_data in response.get("calendars", {}).items():
        busy_by_calendar[cal_id] = [
            (datetime.fromisoformat(b["start"]), datetime.fromisoformat(b["end"]))
            for b in cal_data.get("busy", [])
        ]
    return busy_by_calendar


async def insert_event(
    calendar_id: str,
    summary: str,
    description: str,
    start: datetime,
    end: datetime,
    attendees: list[str],
) -> dict[str, Any]:
    service = await _get_service_async()

    def _call() -> dict[str, Any]:
        body = {
            "summary": summary,
            "description": description,
            "start": {"dateTime": start.isoformat()},
            "end": {"dateTime": end.isoformat()},
            "attendees": [{"email": email} for email in attendees],
        }
        result: dict[str, Any] = (
            service.events().insert(calendarId=calendar_id, body=body, sendUpdates="all").execute()
        )
        return result

    return await asyncio.to_thread(_call)
