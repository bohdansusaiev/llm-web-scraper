"""arXiv discovery provider. Free, no API key, always open access.
API docs: https://arxiv.org/help/api/user-manual

Why arXiv for this thesis:
- Every paper is open access — landing pages at arxiv.org/abs/{id} are ALWAYS
  scrapable. Zero paywalls, zero bot protection, zero login walls.
- Has full structured abstracts in the API response — no shallow metadata.
- Best coverage for CS, ML, AI, Physics, Mathematics topics.
- Directly supports the thesis claim: open-source data + adaptive LLM extraction.

Uses stdlib xml.etree.ElementTree — no extra dependency."""
import logging
import xml.etree.ElementTree as ET
from typing import Optional

import httpx

from app.config import HTTP_TIMEOUT
from app.models.discovery import DiscoveredPaper
from app.services.discovery.base import DiscoveryProvider

logger = logging.getLogger(__name__)

BASE = "https://export.arxiv.org/api/query"
_ATOM = "http://www.w3.org/2005/Atom"
_ARXIV = "http://arxiv.org/schemas/atom"


def _strip_version(arxiv_id: str) -> str:
    """'2301.12345v3' → '2301.12345'"""
    parts = arxiv_id.rsplit("v", 1)
    return parts[0] if len(parts) == 2 and parts[1].isdigit() else arxiv_id


class ArXivProvider(DiscoveryProvider):
    name = "arxiv"

    async def search(
        self,
        topic: str,
        limit: int = 30,
        min_year: Optional[int] = None,
    ) -> list[DiscoveredPaper]:
        params: dict[str, str | int] = {
            "search_query": f"all:{topic}",
            "max_results": min(limit, 100),
            "sortBy": "relevance",
            "sortOrder": "descending",
        }

        try:
            async with httpx.AsyncClient(timeout=HTTP_TIMEOUT) as client:
                r = await client.get(BASE, params=params)
            r.raise_for_status()
        except (httpx.HTTPError, ValueError) as e:
            logger.warning("arXiv search failed for %r: %s", topic, e)
            return []

        try:
            root = ET.fromstring(r.text)
        except ET.ParseError as e:
            logger.warning("arXiv XML parse error: %s", e)
            return []

        out: list[DiscoveredPaper] = []
        for entry in root.findall(f"{{{_ATOM}}}entry"):
            try:
                out.append(self._parse(entry))
            except Exception as e:
                logger.debug("arXiv parse error: %s", e)

        if min_year:
            out = [p for p in out if p.publication_year is None or p.publication_year >= min_year]
        return out

    @staticmethod
    def _parse(entry: ET.Element) -> DiscoveredPaper:
        raw_id = (entry.findtext(f"{{{_ATOM}}}id") or "").strip()
        # e.g. http://arxiv.org/abs/2301.12345v1 → 2301.12345
        arxiv_id = _strip_version(raw_id.split("/abs/")[-1]) if "/abs/" in raw_id else ""

        title = (entry.findtext(f"{{{_ATOM}}}title") or "").strip().replace("\n", " ")
        abstract = (entry.findtext(f"{{{_ATOM}}}summary") or "").strip().replace("\n", " ")

        published = (entry.findtext(f"{{{_ATOM}}}published") or "")[:4]
        year = int(published) if published.isdigit() else None

        authors = []
        for a in entry.findall(f"{{{_ATOM}}}author"):
            name = (a.findtext(f"{{{_ATOM}}}name") or "").strip()
            if name:
                authors.append(name)

        # Primary category as venue (e.g. "cs.LG", "stat.ML")
        cat_el = entry.find(f"{{{_ARXIV}}}primary_category")
        category = cat_el.get("term") if cat_el is not None else None

        # Always use the abs page for extraction — never PDF.
        # arxiv.org/abs/{id} is always accessible, always has the full abstract.
        landing = f"https://arxiv.org/abs/{arxiv_id}" if arxiv_id else None

        return DiscoveredPaper(
            source="arxiv",
            doi=None,
            title=title,
            authors=authors,
            publication_year=year,
            venue=category,
            abstract=abstract,
            landing_url=landing,
            pdf_url=None,  # skip PDF — abs page gives us everything we need
            citation_count=None,
            is_open_access=True,
        )
