from __future__ import annotations

import pytest

from src.services import semantic_chunking as semantic_chunking_module
from src.services.semantic_chunking import semantic_chunk, split_into_sentences


def test_split_into_sentences_basic() -> None:
    text = "The road project is delayed. Contractors cited monsoon rains. Water supply is next."
    sentences = split_into_sentences(text)
    assert sentences == [
        "The road project is delayed.",
        "Contractors cited monsoon rains.",
        "Water supply is next.",
    ]


def test_split_into_sentences_empty() -> None:
    assert split_into_sentences("") == []
    assert split_into_sentences("   ") == []


@pytest.mark.asyncio
async def test_semantic_chunk_cuts_at_topic_shift(monkeypatch: pytest.MonkeyPatch) -> None:
    text = (
        "Road resurfacing is delayed. The contractor blamed heavy rain. "
        "Water pressure is low in Sector 15. The pump station needs inspection."
    )

    # Sentences 0-1 share a topic (roads); sentences 2-3 share a different
    # topic (water) — fake embeddings make that similarity gap explicit.
    fake_vectors = {
        "Road resurfacing is delayed.": [1.0, 0.0, 0.0],
        "The contractor blamed heavy rain.": [0.95, 0.05, 0.0],
        "Water pressure is low in Sector 15.": [0.0, 0.0, 1.0],
        "The pump station needs inspection.": [0.0, 0.05, 0.95],
    }

    async def fake_embed_texts(texts: list[str]) -> list[list[float]]:
        return [fake_vectors[t] for t in texts]

    monkeypatch.setattr(semantic_chunking_module, "embed_texts", fake_embed_texts)

    chunks = await semantic_chunk(text, similarity_threshold=0.5)

    assert len(chunks) == 2
    assert "Road resurfacing" in chunks[0]
    assert "contractor blamed heavy rain" in chunks[0]
    assert "Water pressure" in chunks[1]
    assert "pump station" in chunks[1]


@pytest.mark.asyncio
async def test_semantic_chunk_single_sentence_no_embedding_call(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def fail_if_called(texts: list[str]) -> list[list[float]]:
        raise AssertionError("embed_texts should not be called for a single sentence")

    monkeypatch.setattr(semantic_chunking_module, "embed_texts", fail_if_called)

    chunks = await semantic_chunk("Just one sentence here.")
    assert chunks == ["Just one sentence here."]
