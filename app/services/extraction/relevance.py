"""LLM-based relevance scoring of discovered papers against the user's topic.

One batched call per query — much cheaper than per-paper. Returns scores
in [0, 1]; pipeline applies threshold + sort + topK."""
import json
import logging
from typing import Sequence

from app.core.llm_extractor import extract
from app.core.prompts import RELEVANCE_FILTER_INSTRUCTION
from app.models.discovery import DiscoveredPaper

logger = logging.getLogger(__name__)


async def score_relevance(
    topic: str,
    papers: Sequence[DiscoveredPaper],
) -> dict[int, float]:
    """Return {paper_index: score} for each paper. Indexes are positional."""
    if not papers:
        return {}

    # Build a compact candidate list — title + first 400 chars of abstract.
    candidates = []
    for i, p in enumerate(papers):
        abs_short = (p.abstract or "")[:400]
        candidates.append({
            "id": i,
            "title": p.title[:300],
            "abstract": abs_short,
            "year": p.publication_year,
        })

    user_payload = json.dumps({
        "topic": topic,
        "candidates": candidates,
    }, ensure_ascii=False)

    result = await extract(
        markdown=user_payload,
        instruction=RELEVANCE_FILTER_INSTRUCTION,
        schema={
            "type": "object",
            "properties": {
                "scores": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "integer"},
                            "score": {"type": "number"},
                        },
                        "required": ["id", "score"],
                    },
                }
            },
            "required": ["scores"],
        },
    )

    if not result.success:
        logger.warning("relevance scoring failed: %s — falling back to uniform 0.5", result.error)
        return {i: 0.5 for i in range(len(papers))}

    out: dict[int, float] = {}
    items: list | None = None
    data = result.data
    if isinstance(data, dict):
        scores = data.get("scores")
        if isinstance(scores, list):
            items = scores
        else:
            # LLM returned a different top-level shape — recover any list-of-dict
            for v in data.values():
                if isinstance(v, list):
                    items = v
                    break
    elif isinstance(data, list):
        items = data
    for entry in (items or []):
        try:
            idx = int(entry["id"])
            score = float(entry["score"])
            if 0 <= idx < len(papers):
                out[idx] = max(0.0, min(1.0, score))
        except (KeyError, TypeError, ValueError):
            continue

    # Fill in any missing indices with a neutral score.
    for i in range(len(papers)):
        out.setdefault(i, 0.5)
    return out
