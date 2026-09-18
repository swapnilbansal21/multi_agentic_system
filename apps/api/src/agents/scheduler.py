def run_scheduler_agent(payload: dict) -> dict:
    attendees = payload.get("attendees", [])
    return {
        "agent": "scheduler",
        "suggested_slots": [
            {"start": "2026-09-22T15:00:00+05:30", "confidence": 0.9},
            {"start": "2026-09-23T16:00:00+05:30", "confidence": 0.75},
            {"start": "2026-09-24T11:00:00+05:30", "confidence": 0.6},
        ],
        "attendees": attendees,
    }
