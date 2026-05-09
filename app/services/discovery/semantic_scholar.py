"""Semantic Scholar client. Free, optional API key, very strong on CS papers.
Docs: https://api.semanticscholar.org/api-docs/

Less reliable than OpenAlex (rate-limited harder on free tier) but
complementary — useful when topic is CS/ML."""
import logging
from typing import Optional

import httpx

from app.config import SEMANTIC_SCHOLAR_API_KEY, HTTP_TIMEOUT
from app.models.discovery import DiscoveredPaper
from app.services.discovery.base import DiscoveryProvider
from app.utils.dedupe import normalize_doi

logger = logging.getLogger(__name__)

BASE = "https://api.semanticscholar.org/graph/v1/paper/search"


class SemanticScholarProvider(DiscoveryProvider):
    name = "semantic_scholar"

    async def search(
        self,
        topic: str,
        limit: int = 30,
        min_year: Optional[int] = None,
    ) -> list[DiscoveredPaper]:
        params: dict[str, str | int] = {
            "query": topic,
            "limit": min(limit, 50),
            "fields": "title,authors,abstract,year,venue,externalIds,citationCount,openAccessPdf,url",
        }
        if min_year:
            params["year"] = f"{min_year}-"

        headers = {}
        if SEMANTIC_SCHOLAR_API_KEY:
            headers["x-api-key"] = SEMANTIC_SCHOLAR_API_KEY

        try:
            async with httpx.AsyncClient(timeout=HTTP_TIMEOUT) as client:
                r = await client.get(BASE, params=params, headers=headers)
            r.raise_for_status()
            data = r.json().get("data", [])
        except (httpx.HTTPError, ValueError) as e:
            logger.warning("Semantic Scholar search failed for %r: %s", topic, e)
            return []

        out: list[DiscoveredPaper] = []
        for it in data:
            try:
                out.append(self._parse(it))
            except Exception as e:
                logger.debug("Semantic Scholar parse error: %s", e)
        return out

    @staticmethod
    def _parse(it: dict) -> DiscoveredPaper:
        ext = it.get("externalIds") or {}
        oa = it.get("openAccessPdf") or {}
        return DiscoveredPaper(
            source="semantic_scholar",
            doi=normalize_doi(ext.get("DOI")),
            title=it.get("title") or "",
            authors=[a.get("name", "") for a in (it.get("authors") or []) if a.get("name")],
            publication_year=it.get("year"),
            venue=it.get("venue") or None,
            abstract=it.get("abstract") or "",
            landing_url=it.get("url"),
            pdf_url=oa.get("url"),
            citation_count=it.get("citationCount"),
            is_open_access=bool(oa.get("url")),
        )
