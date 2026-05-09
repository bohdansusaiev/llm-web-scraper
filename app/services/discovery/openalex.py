"""OpenAlex client. Free, no key required, ~100M+ works indexed.
Docs: https://docs.openalex.org/api-entities/works/search-works

Why OpenAlex first: best coverage (incl. arXiv, PMC, publishers), returns
abstracts as inverted-index, has open_access.oa_url, and is fastest of the three."""
import logging
from typing import Optional

import httpx

from app.config import OPENALEX_EMAIL, HTTP_TIMEOUT
from app.models.discovery import DiscoveredPaper
from app.services.discovery.base import DiscoveryProvider
from app.utils.dedupe import normalize_doi

logger = logging.getLogger(__name__)

BASE = "https://api.openalex.org/works"


def _reconstruct_abstract(inverted: dict | None) -> str:
    """OpenAlex returns abstracts as an inverted index {word: [positions]} for
    copyright reasons. Reconstruct word order."""
    if not inverted:
        return ""
    positions: list[tuple[int, str]] = []
    for word, idxs in inverted.items():
        for i in idxs:
            positions.append((i, word))
    positions.sort()
    return " ".join(w for _, w in positions)


class OpenAlexProvider(DiscoveryProvider):
    name = "openalex"

    async def search(
        self,
        topic: str,
        limit: int = 30,
        min_year: Optional[int] = None,
    ) -> list[DiscoveredPaper]:
        params: dict[str, str | int] = {
            "search": topic,
            "per-page": min(limit, 50),
            "sort": "relevance_score:desc",
        }
        filters = []
        if min_year:
            filters.append(f"from_publication_date:{min_year}-01-01")
        if filters:
            params["filter"] = ",".join(filters)
        if OPENALEX_EMAIL:
            params["mailto"] = OPENALEX_EMAIL

        try:
            async with httpx.AsyncClient(timeout=HTTP_TIMEOUT) as client:
                r = await client.get(BASE, params=params)
            r.raise_for_status()
            payload = r.json()
        except (httpx.HTTPError, ValueError) as e:
            logger.warning("OpenAlex search failed for %r: %s", topic, e)
            return []

        out: list[DiscoveredPaper] = []
        for work in payload.get("results", []):
            try:
                out.append(self._parse(work))
            except Exception as e:  # malformed item — skip, keep the rest
                logger.debug("OpenAlex parse error: %s", e)
        return out

    @staticmethod
    def _parse(w: dict) -> DiscoveredPaper:
        oa = w.get("open_access") or {}
        primary_loc = w.get("primary_location") or {}
        host_venue = (w.get("host_venue") or {}).get("display_name") \
                  or (primary_loc.get("source") or {}).get("display_name")
        authors = []
        for a in (w.get("authorships") or []):
            name = (a.get("author") or {}).get("display_name")
            if name:
                authors.append(name)
        landing = primary_loc.get("landing_page_url")
        pdf = oa.get("oa_url") or primary_loc.get("pdf_url")
        return DiscoveredPaper(
            source="openalex",
            doi=normalize_doi(w.get("doi")),
            title=w.get("title") or w.get("display_name") or "",
            authors=authors,
            publication_year=w.get("publication_year"),
            venue=host_venue,
            abstract=_reconstruct_abstract(w.get("abstract_inverted_index")),
            landing_url=landing,
            pdf_url=pdf,
            citation_count=w.get("cited_by_count"),
            is_open_access=bool(oa.get("is_oa")),
        )
