"""Crossref client. Free, no key, very wide DOI coverage.
Docs: https://api.crossref.org/swagger-ui/index.html

Crossref complements OpenAlex: smaller abstracts but wider DOI catalog,
useful as a second source for dedupe and as a fallback."""
import logging
from typing import Optional

import httpx

from app.config import OPENALEX_EMAIL, HTTP_TIMEOUT
from app.models.discovery import DiscoveredPaper
from app.services.discovery.base import DiscoveryProvider
from app.utils.dedupe import normalize_doi

logger = logging.getLogger(__name__)

BASE = "https://api.crossref.org/works"


class CrossrefProvider(DiscoveryProvider):
    name = "crossref"

    async def search(
        self,
        topic: str,
        limit: int = 30,
        min_year: Optional[int] = None,
    ) -> list[DiscoveredPaper]:
        params: dict[str, str | int] = {
            "query": topic,
            "rows": min(limit, 50),
            "select": ("DOI,title,author,abstract,issued,container-title,"
                       "is-referenced-by-count,URL,link"),
            "sort": "relevance",
        }
        if min_year:
            params["filter"] = f"from-pub-date:{min_year}-01-01"

        # Crossref appreciates a mailto for the polite pool.
        headers = {}
        if OPENALEX_EMAIL:
            headers["User-Agent"] = f"LLMScraperDiploma/1.0 (mailto:{OPENALEX_EMAIL})"

        try:
            async with httpx.AsyncClient(timeout=HTTP_TIMEOUT) as client:
                r = await client.get(BASE, params=params, headers=headers)
            r.raise_for_status()
            items = r.json().get("message", {}).get("items", [])
        except (httpx.HTTPError, ValueError) as e:
            logger.warning("Crossref search failed for %r: %s", topic, e)
            return []

        out: list[DiscoveredPaper] = []
        for it in items:
            try:
                out.append(self._parse(it))
            except Exception as e:
                logger.debug("Crossref parse error: %s", e)
        return out

    @staticmethod
    def _parse(it: dict) -> DiscoveredPaper:
        title_list = it.get("title") or []
        title = title_list[0] if title_list else ""
        container = it.get("container-title") or []
        venue = container[0] if container else None
        authors = []
        for a in (it.get("author") or []):
            given = (a.get("given") or "").strip()
            family = (a.get("family") or "").strip()
            full = (given + " " + family).strip()
            if full:
                authors.append(full)
        year = None
        issued = (it.get("issued") or {}).get("date-parts") or []
        if issued and issued[0]:
            year = issued[0][0]

        # Crossref's "abstract" is JATS XML; strip tags as a quick approximation.
        import re as _re
        abstract = _re.sub(r"<[^>]+>", "", it.get("abstract") or "").strip()

        # Try to find a free PDF in the link blocks.
        pdf_url = None
        for link in (it.get("link") or []):
            if link.get("content-type") == "application/pdf":
                pdf_url = link.get("URL")
                break

        return DiscoveredPaper(
            source="crossref",
            doi=normalize_doi(it.get("DOI")),
            title=title,
            authors=authors,
            publication_year=year,
            venue=venue,
            abstract=abstract,
            landing_url=it.get("URL"),
            pdf_url=pdf_url,
            citation_count=it.get("is-referenced-by-count"),
            is_open_access=bool(pdf_url),  # heuristic — Crossref doesn't say directly
        )
