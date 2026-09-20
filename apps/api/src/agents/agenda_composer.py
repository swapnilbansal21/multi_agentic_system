from __future__ import annotations

from typing import Any

from openai import AsyncAzureOpenAI
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import settings
from src.services.rag_retrieval import retrieve


def _get_chat_client() -> AsyncAzureOpenAI:
    return AsyncAzureOpenAI(
        azure_endpoint=settings.azure_openai_endpoint,
        api_key=settings.azure_openai_api_key,
        api_version=settings.azure_openai_api_version,
    )


async def run_agenda_composer_agent(
    session: AsyncSession, payload: dict[str, Any]
) -> dict[str, Any]:
    topic = payload.get("topic", "")

    past_chunks = await retrieve(session, corpus="past_meetings", query_text=topic, top_k=5)
    context_text = "\n\n---\n\n".join(chunk.content for chunk in past_chunks)

    client = _get_chat_client()
    response = await client.chat.completions.create(
        model=settings.azure_openai_deployment,
        messages=[
            {
                "role": "system",
                "content": (
                    "You draft meeting agendas for Indian government officials. "
                    "Use the provided past-meeting context if relevant. Output a "
                    "5-point agenda, bilingual: each point in English then Hindi."
                ),
            },
            {
                "role": "user",
                "content": f"Topic: {topic}\n\nPast meeting context:\n{context_text or '(none found)'}",
            },
        ],
    )
    agenda_draft = response.choices[0].message.content

    return {
        "agent": "agenda_composer",
        "topic": topic,
        "agenda_draft": agenda_draft,
        "grounded_on_chunks": len(past_chunks),
        "retrieved_context_texts": [chunk.content for chunk in past_chunks],
    }
