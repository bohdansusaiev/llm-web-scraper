"""Phase 2 deep extraction — fetch one paper's URL, extract a ScientificPaper.

Composes: crawler.fetch_markdown -> llm_extractor.extract with the scientific schema.
Detects login/paywall walls and reports them via failure_reason."""
import logging
from typing import Optional

from app.core.crawler import fetch_markdown, detect_block_reason, truncate_markdown
from app.core.llm_extractor import extract as llm_extract
from app.core.prompts import SCIENTIFIC_PAPER_INSTRUCTION
from app.db.cache import make_cache_key, get_cached, put_cached
from app.models.catalog import (
    ScientificPaper, Author, ExtractionFailureReason,
)
from app.models.discovery import DiscoveredPaper

logger = logging.getLogger(__name__)


# Schema given to the LLM for Phase 2. Matches ScientificPaper text fields
# (we fill identity fields from the discovery record afterwards).
PAPER_LLM_SCHEMA = {
    "type": "object",
    "properties": {
        "title": {"type": "string"},
        "authors": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "affiliation": {"type": "string"},
                    "orcid": {"type": "string"},
                },
                "required": ["name"],
            },
        },
        "abstract": {"type": "string"},
        "methodology": {"type": "string"},
        "conclusions": {"type": "string"},
        "keywords": {"type": "array", "items": {"type": "string"}},
        "publication_year": {"type": ["integer", "null"]},
        "venue": {"type": ["string", "null"]},
        "doi": {"type": ["string", "null"]},
        "image_url": {"type": "string",
            "description": "URL of a representative image (paper figure, journal logo, etc) or empty string"},
    },
    "required": ["title", "abstract", "methodology", "conclusions", "keywords"],
}


async def extract_paper(
    discovered: DiscoveredPaper,
    *,
    use_cache: bool = True,
    relevance_score: float = 0.0,
) -> ScientificPaper:
    """Run Phase 2 on one DiscoveredPaper. Returns a ScientificPaper, possibly
    with failure_reason set if extraction couldn't complete."""
    base = _seed_from_discovery(discovered, relevance_score)

    url = discovered.best_url
    if not url:
        # No URL to crawl — return whatever the API gave us.
        base.extraction_source = "api"
        return base

    # Cache check
    cache_key = make_cache_key(url, PAPER_LLM_SCHEMA, language="en")
    if use_cache:
        hit = get_cached(cache_key)
        if hit:
            data, _md_preview = hit
            return _merge_extraction(base, data, source_label="cache")

    # Fetch markdown
    crawl = await fetch_markdown(url)
    if not crawl.success:
        base.failure_reason = ExtractionFailureReason.NETWORK_ERROR
        base.extraction_source = "api"
        logger.info("crawl failed for %s: %s", url, crawl.error)
        return base

    block = detect_block_reason(crawl.markdown)
    if block == "login_wall":
        base.failure_reason = ExtractionFailureReason.LOGIN_WALL
        base.extraction_source = "api"
        return base
    if block == "paywall":
        base.failure_reason = ExtractionFailureReason.PAYWALL
        base.extraction_source = "api"
        return base
    if block == "bot_protection":
        base.failure_reason = ExtractionFailureReason.BOT_PROTECTION
        base.extraction_source = "api"
        return base
    if block == "extraction_empty":
        base.failure_reason = ExtractionFailureReason.EXTRACTION_EMPTY
        base.extraction_source = "api"
        return base

    md = truncate_markdown(crawl.markdown)
    llm = await llm_extract(
        markdown=md,
        schema=PAPER_LLM_SCHEMA,
        instruction=SCIENTIFIC_PAPER_INSTRUCTION,
    )
    if not llm.success:
        base.failure_reason = ExtractionFailureReason.LLM_ERROR
        base.extraction_source = "api"
        logger.info("LLM failed for %s: %s", url, llm.error)
        return base

    paper = _merge_extraction(base, llm.data, source_label="crawl")
    put_cached(cache_key, url, llm.data, markdown_preview=md[:500])
    return paper


def _seed_from_discovery(d: DiscoveredPaper, score: float) -> ScientificPaper:
    return ScientificPaper(
        doi=d.doi,
        title=d.title,
        authors=[Author(name=n) for n in d.authors],
        publication_year=d.publication_year,
        venue=d.venue,
        url=d.best_url or d.landing_url or "",
        abstract=d.abstract or "",
        methodology="",
        conclusions="",
        keywords=[],
        citation_count=d.citation_count,
        is_open_access=d.is_open_access,
        relevance_score=score,
        extraction_source="",
        failure_reason=ExtractionFailureReason.NONE,
        language="en",
    )


def _merge_extraction(
    base: ScientificPaper,
    llm_data: dict,
    source_label: str,
) -> ScientificPaper:
    """Apply LLM-extracted fields on top of the discovery seed.
    LLM wins on content fields (abstract/methodology/etc.) only when non-empty,
    so a sparse LLM result doesn't erase good API data."""
    def _str(v) -> str:
        return v if isinstance(v, str) else ""

    new_abstract = _str(llm_data.get("abstract")).strip()
    if new_abstract and len(new_abstract) > len(base.abstract):
        base.abstract = new_abstract

    base.methodology = _str(llm_data.get("methodology")).strip()
    base.conclusions = _str(llm_data.get("conclusions")).strip()

    kw = llm_data.get("keywords") or []
    if isinstance(kw, list):
        base.keywords = [str(k).lower().strip() for k in kw if str(k).strip()]

    # LLM-supplied identity only if missing from API
    if not base.title and isinstance(llm_data.get("title"), str):
        base.title = llm_data["title"].strip()
    if not base.publication_year and isinstance(llm_data.get("publication_year"), int):
        base.publication_year = llm_data["publication_year"]
    if not base.venue and isinstance(llm_data.get("venue"), str):
        base.venue = llm_data["venue"]
    if not base.doi and isinstance(llm_data.get("doi"), str):
        base.doi = llm_data["doi"].lower().strip() or None

    img = llm_data.get("image_url")
    if isinstance(img, str) and img.strip().startswith("http"):
        base.image_url = img.strip()

    # Authors: only override if LLM gave us a longer list than the API
    llm_authors = llm_data.get("authors") or []
    if isinstance(llm_authors, list) and len(llm_authors) > len(base.authors):
        merged_authors: list[Author] = []
        for a in llm_authors:
            if isinstance(a, dict) and a.get("name"):
                merged_authors.append(Author(
                    name=a["name"],
                    affiliation=a.get("affiliation") or None,
                    orcid=a.get("orcid") or None,
                ))
            elif isinstance(a, str) and a.strip():
                merged_authors.append(Author(name=a.strip()))
        if merged_authors:
            base.authors = merged_authors

    base.extraction_source = source_label
    base.failure_reason = ExtractionFailureReason.NONE
    if not base.abstract.strip() and not base.methodology.strip() and not base.conclusions.strip():
        base.failure_reason = ExtractionFailureReason.EXTRACTION_EMPTY
    return base
