def run_agenda_composer_agent(payload: dict) -> dict:
    topic = payload.get("topic", "")
    return {
        "agent": "agenda_composer",
        "topic": topic,
        "agenda_draft": [f"Discuss: {topic}", "Review action items", "Next steps"],
    }
