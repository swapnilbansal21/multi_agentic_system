from __future__ import annotations

import math
import re

from src.services.embeddings import embed_texts

_SENTENCE_SPLIT = re.compile(r"(?<=[.!?])\s+(?=[A-Z])")

DEFAULT_SIMILARITY_THRESHOLD = 0.75


def split_into_sentences(text: str) -> list[str]:
    text = text.strip()
    if not text:
        return []
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    sentences: list[str] = []
    for para in paragraphs:
        sentences.extend(s.strip() for s in _SENTENCE_SPLIT.split(para) if s.strip())
    return sentences


def _cosine_similarity(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b, strict=True))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(y * y for y in b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


async def semantic_chunk(
    text: str, similarity_threshold: float = DEFAULT_SIMILARITY_THRESHOLD
) -> list[str]:
    """Semantic chunking: embed each sentence, cut a new chunk whenever
    similarity to the previous sentence drops below `similarity_threshold`
    (a topic shift). Used for documents without structural headings — unlike
    `chunk_meeting_minutes`, which relies on 'Agenda Item N:' markers."""
    sentences = split_into_sentences(text)
    if not sentences:
        return []
    if len(sentences) == 1:
        return sentences

    embeddings = await embed_texts(sentences)

    chunks: list[str] = []
    current_chunk_sentences = [sentences[0]]

    for i in range(1, len(sentences)):
        similarity = _cosine_similarity(embeddings[i - 1], embeddings[i])
        if similarity < similarity_threshold:
            chunks.append(" ".join(current_chunk_sentences))
            current_chunk_sentences = [sentences[i]]
        else:
            current_chunk_sentences.append(sentences[i])

    chunks.append(" ".join(current_chunk_sentences))
    return chunks
