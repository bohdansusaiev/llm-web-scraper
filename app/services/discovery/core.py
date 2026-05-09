"""CORE open access aggregator client.
API docs: https://api.core.ac.uk/v3/docs

CORE indexes 200M+ open access papers from 10 000+ repositories worldwide
(institutional repositories, university archives, preprint servers). Unlike
CrossRef, CORE papers always have full text available — that's the whole point
of the aggregator. This makes it an ideal discovery source for the thesis:
all discovered papers can actually be crawled and deeply extracted.

Requires a free API key: https://core.ac.uk/services/api"""
import logging
from typing import Any, Optional

import httpx

from app.config import CORE_API_KEY, HTTP_TIMEOUT
from app.models.discovery import DiscoveredPaper
from app.services.discovery.base import DiscoveryProvider
from app.utils.dedupe import normalize_doi

logger = logging.getLogger(__name__)

BASE = "https://api.core.ac.uk/v3/search/works"


class CoreProvider(DiscoveryProvider):
    name = "core"

    async def search(
        self,
        topic: str,
        limit: int = 30,
        min_year: Optional[int] = None,
    ) -> list[DiscoveredPaper]:
        if not CORE_API_KEY:
            logger.warning("CORE_API_KEY not set — skipping CORE provider")
            return []

        params: dict[str, Any] = {
            "q": topic,
            "limit": min(limit, 100),
            "offset": 0,
        }

        try:
            async with httpx.AsyncClient(timeout=HTTP_TIMEOUT) as client:
                r = await client.get(
                    BASE,
                    params=params,
                    headers={"Authorization": f"Bearer {CORE_API_KEY}"},
                )
            r.raise_for_status()
            data = r.json()
        except (httpx.HTTPError, ValueError) as e:
            logger.warning("CORE search failed for %r: %s", topic, e)
            return []

        out: list[DiscoveredPaper] = []
        for item in data.get("results", []):
            try:
                out.append(self._parse(item))
            except Exception as e:
                logger.debug("CORE parse error: %s", e)

        if min_year:
            out = [p for p in out if p.publication_year is None or p.publication_year >= min_year]
        return out

    @staticmethod
    def _parse(it: dict) -> DiscoveredPaper:
        core_id = it.get("id")

        authors = []
        for a in (it.get("authors") or []):
            name = (a.get("name") or "").strip()
            if name:
                authors.append(name)

        journals = it.get("journals") or []
        venue = journals[0].get("title") if journals else it.get("publisher") or None

        # Prefer a non-PDF full-text URL for Crawl4AI/Jina; fall back to CORE works page.
        download_url: str = it.get("downloadUrl") or ""
        source_urls: list[str] = it.get("sourceFulltextUrls") or []
        html_url = next(
            (u for u in source_urls if u and not u.lower().endswith(".pdf")),
            None,
        )
        if not html_url and download_url and not download_url.lower().endswith(".pdf"):
            html_url = download_url
        # Always fall back to the CORE works page (always accessible, always HTML)
        landing = html_url or (f"https://core.ac.uk/works/{core_id}" if core_id else None)

        return DiscoveredPaper(
            source="core",
            doi=normalize_doi(it.get("doi")),
            title=(it.get("title") or "").strip(),
            authors=authors,
            publication_year=it.get("yearPublished"),
            venue=venue,
            abstract=(it.get("abstract") or "").strip(),
            landing_url=landing,
            pdf_url=None,  # skip PDF — HTML page gives us enough for extraction
            citation_count=None,
            is_open_access=True,  # CORE only indexes open access content
        )
