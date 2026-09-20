"""Phase 1 (runs in the main app venv): executes our real RAG pipeline
(retrieve + agenda_composer) against the curated eval set and writes
predictions to a JSON file. Phase 2 (ragas_eval.py, separate venv) reads
that file and scores it — kept apart because `ragas` conflicts with our
app's langgraph dependency version (see conversation: ragas 0.4.3 pulls an
incompatible langchain-core).

Run with: .venv/Scripts/python.exe -m src.evals.generate_rag_predictions
"""

from __future__ import annotations

import asyncio
import json
from pathlib import Path

from src.agents.agenda_composer import run_agenda_composer_agent
from src.db.session import async_session_factory
from src.evals.rag_eval_dataset import RAG_EVAL_CASES

OUTPUT_PATH = Path(__file__).parent / "rag_eval_predictions.json"


async def main() -> None:
    predictions = []

    async with async_session_factory() as session:
        for case in RAG_EVAL_CASES:
            result = await run_agenda_composer_agent(session, {"topic": case["question"]})

            predictions.append(
                {
                    "question": case["question"],
                    "ground_truth": case["ground_truth"],
                    "answer": result["agenda_draft"],
                    "contexts": result.get("retrieved_context_texts", []),
                }
            )
            print(f"done: {case['question']}")

    OUTPUT_PATH.write_text(json.dumps(predictions, indent=2, ensure_ascii=False))
    print(f"\nWrote {len(predictions)} predictions to {OUTPUT_PATH}")


if __name__ == "__main__":
    asyncio.run(main())
