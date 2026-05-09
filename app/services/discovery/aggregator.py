"""Run multiple discovery providers in parallel, merge, dedupe.

Dedupe strategy:
1. Group by normalized DOI when present.
2. For papers without DOI, group by normalized title (lossy but acceptable).
3. When merging duplicates, prefer the record with: more authors, more
   abstract text, an open-access URL, higher citation count."""
import asyncio
import logging
from typing import Optional

from app.models.discovery import DiscoveredPaper
from app.services.discovery.arxiv import ArXivProvider
from app.services.discovery.base import DiscoveryProvider
from app.services.discovery.core import CoreProvider
from app.services.discovery.openalex import OpenAlexProvider
from app.services.discovery.crossref import CrossrefProvider
from app.services.discovery.semantic_scholar import SemanticScholarProvider
from app.utils.dedupe import normalize_title

logger = logging.getLogger(__name__)


PROVIDERS: dict[str, type[DiscoveryProvider]] = {
    "openalex": OpenAlexProvider,
    "semantic_scholar": SemanticScholarProvider,
    "arxiv": ArXivProvider,
    "core": CoreProvider,
    # crossref: DOI registry, rarely has abstracts, landing URLs go to paywalls.
    # Available for power users but off by default.
    "crossref": CrossrefProvider,
}


JUNK_PHRASES = (
    "written purely by ai",
    "ai for entertainment",
    "not intended for peer review",
    "this publication is not peer reviewed",
    "for entertainment purposes only",
    "for fun, not for citation",
)


def _is_junk(p: DiscoveredPaper) -> bool:
    """Drop obvious AI-generated entertainment papers before they reach
    relevance scoring. Saves LLM tokens and keeps catalogs clean."""
    text = (p.title + " " + (p.abstract or "")).lower()
    return any(phrase in text for phrase in JUNK_PHRASES)


async def discover(
    topic: str,
    providers: list[str],
    limit_per_provider: int = 30,
    min_year: Optional[int] = None,
) -> list[DiscoveredPaper]:
    """Fan out across providers in parallel, merge results, dedupe."""
    selected = [PROVIDERS[p]() for p in providers if p in PROVIDERS]
    if not selected:
        return []

    tasks = [p.search(topic, limit_per_provider, min_year) for p in selected]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    all_papers: list[DiscoveredPaper] = []
    for prov, res in zip(selected, results):
        if isinstance(res, Exception):
            logger.warning("provider %s raised: %s", prov.name, res)
            continue
        all_papers.extend(res)

    # Filter obvious junk before dedupe — both faster and avoids a junk paper
    # being chosen as the "richer" record during merge.
    cleaned = [p for p in all_papers if not _is_junk(p)]
    if len(cleaned) < len(all_papers):
        logger.info("filtered %d junk papers", len(all_papers) - len(cleaned))
    return _dedupe(cleaned)


def _dedupe(papers: list[DiscoveredPaper]) -> list[DiscoveredPaper]:
    """Merge duplicates by DOI first, then by normalized title."""
    by_key: dict[str, DiscoveredPaper] = {}
    for p in papers:
        key = p.doi if p.doi else f"title::{normalize_title(p.title)}"
        if not key.replace("title::", "").strip():
            continue  # empty key — drop record
        existing = by_key.get(key)
        if existing is None:
            by_key[key] = p
        else:
            by_key[key] = _merge(existing, p)
    return list(by_key.values())


def _merge(a: DiscoveredPaper, b: DiscoveredPaper) -> DiscoveredPaper:
    """Combine two records of the same paper, preferring richer fields."""
    return DiscoveredPaper(
        source=f"{a.source}+{b.source}" if a.source != b.source else a.source,
        doi=a.doi or b.doi,
        title=a.title if len(a.title) >= len(b.title) else b.title,
        authors=a.authors if len(a.authors) >= len(b.authors) else b.authors,
        publication_year=a.publication_year or b.publication_year,
        venue=a.venue or b.venue,
        abstract=a.abstract if len(a.abstract) >= len(b.abstract) else b.abstract,
        landing_url=a.landing_url or b.landing_url,
        pdf_url=a.pdf_url or b.pdf_url,
        citation_count=max(a.citation_count or 0, b.citation_count or 0) or None,
        is_open_access=a.is_open_access or b.is_open_access,
    )
