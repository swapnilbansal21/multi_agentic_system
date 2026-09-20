from __future__ import annotations

from typing import Any

from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.rag_chunk import RagChunk
from src.services.chunking import chunk_meeting_minutes
from src.services.embeddings import embed_texts


async def ingest_meeting_minutes(
    session: AsyncSession,
    source_id: str,
    text: str,
    metadata: dict[str, Any],
) -> int:
    """Chunks + embeds meeting minutes and stores them under `source_id`.
    Re-ingesting the same source_id replaces its old chunks (delete-then-insert)
    so edited/updated documents never leave stale chunks behind."""
    chunks = chunk_meeting_minutes(text)

    await session.execute(
        delete(RagChunk).where(
            RagChunk.corpus == "past_meetings", RagChunk.source_id == source_id
        )
    )

    if not chunks:
        await session.commit()
        return 0

    embeddings = await embed_texts(chunks)

    for chunk_text, embedding in zip(chunks, embeddings, strict=True):
        session.add(
            RagChunk(
                corpus="past_meetings",
                source_id=source_id,
                content=chunk_text,
                embedding=embedding,
                chunk_metadata=metadata,
            )
        )

    await session.commit()
    return len(chunks)
