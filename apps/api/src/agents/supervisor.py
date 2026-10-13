from typing import Any, Literal, TypedDict, cast

import instructor
from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph
from openai import AsyncAzureOpenAI
from pydantic import BaseModel

from src.agents.agenda_composer import run_agenda_composer_agent
from src.agents.scheduler import run_scheduler_agent
from src.core.config import settings
from src.db.session import async_session_factory
from src.services.officer_directory import resolve_attendee_emails


class IntentClassification(BaseModel):
    intent: Literal["schedule", "agenda"]
    attendees: list[str] = []
    topic: str = ""


class SupervisorState(TypedDict):
    query: str
    organizer_email: str
    classification: IntentClassification | None
    result: dict[str, Any] | None


def _get_instructor_client() -> instructor.AsyncInstructor:
    azure_client = AsyncAzureOpenAI(
        azure_endpoint=settings.azure_openai_endpoint,
        api_key=settings.azure_openai_api_key,
        api_version="2024-10-21",
    )
    return instructor.from_openai(azure_client)


async def classify_node(state: SupervisorState) -> SupervisorState:
    client = _get_instructor_client()
    classification = await client.chat.completions.create(
        model=settings.azure_openai_deployment,
        response_model=IntentClassification,
        messages=[
            {
                "role": "system",
                "content": (
                    "You classify meeting-related requests into an intent. "
                    "Use 'schedule' when the user wants to schedule/arrange a meeting. "
                    "Use 'agenda' when the user wants an agenda drafted for a topic. "
                    "Extract attendee names/emails and the topic if mentioned."
                ),
            },
            {"role": "user", "content": state["query"]},
        ],
    )
    state["classification"] = classification
    return state


def route_after_classify(state: SupervisorState) -> str:
    classification = state["classification"]
    assert classification is not None
    return classification.intent


async def scheduler_node(state: SupervisorState) -> SupervisorState:
    classification = state["classification"]
    assert classification is not None

    async with async_session_factory() as session:
        attendee_emails = await resolve_attendee_emails(session, classification.attendees)

    payload = {
        "attendees": attendee_emails,
        "topic": classification.topic,
        "organizer_email": state["organizer_email"],
    }
    state["result"] = await run_scheduler_agent(payload)
    return state


async def agenda_node(state: SupervisorState) -> SupervisorState:
    classification = state["classification"]
    assert classification is not None
    payload = {"attendees": classification.attendees, "topic": classification.topic}

    async with async_session_factory() as session:
        state["result"] = await run_agenda_composer_agent(session, payload)
    return state


def build_supervisor_graph() -> (
    CompiledStateGraph[SupervisorState, None, SupervisorState, SupervisorState]
):
    graph = StateGraph(SupervisorState)
    graph.add_node("classify", classify_node)
    graph.add_node("scheduler", scheduler_node)
    graph.add_node("agenda", agenda_node)

    graph.add_edge(START, "classify")
    graph.add_conditional_edges(
        "classify",
        route_after_classify,
        {"schedule": "scheduler", "agenda": "agenda"},
    )
    graph.add_edge("scheduler", END)
    graph.add_edge("agenda", END)

    return graph.compile()


supervisor_graph = build_supervisor_graph()


async def run_supervisor(query: str, organizer_email: str) -> dict[str, Any]:
    final_state = cast(
        SupervisorState,
        await supervisor_graph.ainvoke(
            {
                "query": query,
                "organizer_email": organizer_email,
                "classification": None,
                "result": None,
            }
        ),
    )
    result = final_state["result"]
    assert result is not None
    return result
