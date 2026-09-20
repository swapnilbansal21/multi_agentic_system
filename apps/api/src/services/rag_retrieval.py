from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.rag_chunk import RagChunk
from src.services.embeddings import embed_text

RRF_K = 60


async def _vector_search_ids(
    session: AsyncSession, corpus: str, query_embedding: list[float], limit: int
) -> list[str]:
    stmt = (
        select(RagChunk.id)
        .where(RagChunk.corpus == corpus)
        .order_by(RagChunk.embedding.cosine_distance(query_embedding))
        .limit(limit)
    )
    result = await session.execute(stmt)
    return [str(row[0]) for row in result.all()]


async def _keyword_search_ids(
    session: AsyncSession, corpus: str, query_text: str, limit: int
) -> list[str]:
    tsv = func.to_tsvector("english", RagChunk.content)
    tsq = func.plainto_tsquery("english", query_text)
    rank = func.ts_rank(tsv, tsq)

    stmt = (
        select(RagChunk.id)
        .where(RagChunk.corpus == corpus, tsv.op("@@")(tsq))
        .order_by(rank.desc())
        .limit(limit)
    )
    result = await session.execute(stmt)
    return [str(row[0]) for row in result.all()]


def _reciprocal_rank_fusion(ranked_lists: list[list[str]], k: int = RRF_K) -> list[str]:
    scores: dict[str, float] = {}
    for ranked_ids in ranked_lists:
        for rank, chunk_id in enumerate(ranked_ids, start=1):
            scores[chunk_id] = scores.get(chunk_id, 0.0) + 1.0 / (k + rank)
    return sorted(scores, key=lambda cid: scores[cid], reverse=True)


async def retrieve(
    session: AsyncSession, corpus: str, query_text: str, top_k: int = 5
) -> list[RagChunk]:
    """Advanced/Modular RAG (spec §10): hybrid vector+keyword search, RRF fusion,
    top-k. Fixed pipeline — no LLM-driven retrieval looping (deliberately not
    Agentic RAG, see cost/latency/predictability tradeoffs discussed with user)."""
    query_embedding = await embed_text(query_text)

    vector_ids = await _vector_search_ids(session, corpus, query_embedding, limit=20)
    keyword_ids = await _keyword_search_ids(session, corpus, query_text, limit=20)

    fused_ids = _reciprocal_rank_fusion([vector_ids, keyword_ids])[:top_k]
    if not fused_ids:
        return []

    stmt = select(RagChunk).where(RagChunk.id.in_(fused_ids))
    result = await session.execute(stmt)
    chunks_by_id = {str(chunk.id): chunk for chunk in result.scalars().all()}
    return [chunks_by_id[cid] for cid in fused_ids if cid in chunks_by_id]
