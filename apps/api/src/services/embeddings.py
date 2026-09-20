from __future__ import annotations

from openai import AsyncAzureOpenAI

from src.core.config import settings


def _get_client() -> AsyncAzureOpenAI:
    return AsyncAzureOpenAI(
        azure_endpoint=settings.azure_openai_endpoint,
        api_key=settings.azure_openai_api_key,
        api_version=settings.azure_openai_api_version,
    )


async def embed_text(text: str) -> list[float]:
    client = _get_client()
    response = await client.embeddings.create(
        model=settings.azure_openai_embedding_deployment,
        input=text,
    )
    return response.data[0].embedding


async def embed_texts(texts: list[str]) -> list[list[float]]:
    if not texts:
        return []
    client = _get_client()
    response = await client.embeddings.create(
        model=settings.azure_openai_embedding_deployment,
        input=texts,
    )
    return [item.embedding for item in response.data]
