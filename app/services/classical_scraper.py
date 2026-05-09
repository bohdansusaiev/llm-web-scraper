"""Classical (non-LLM) scraping baseline. Used by the benchmark endpoint to
quantify the gain from LLM-based extraction.

Strategy:
1. httpx GET (no JS rendering — that's the point: classical methods are simpler).
2. trafilatura for main-content extraction + metadata (title, author, date).
3. BeautifulSoup heuristics to fill in fields trafilatura misses.

This is intentionally NOT cleverer than typical scrapers in the wild.
A fancier baseline would muddy the comparison."""
import re
import time
from dataclasses import dataclass
from typing import Any

import httpx
import trafilatura
from bs4 import BeautifulSoup

from app.config import HTTP_TIMEOUT


@dataclass
class ClassicalResult:
    success: bool
    fields: dict[str, Any]
    bytes_downloaded: int
    duration_ms: int
    error: str = ""


def _meta(soup: BeautifulSoup, *names: str) -> str:
    for n in names:
        tag = soup.find("meta", attrs={"name": n}) or soup.find("meta", attrs={"property": n})
        if tag and tag.get("content"):
            return tag["content"].strip()
    return ""


def _extract_keywords_from_meta(soup: BeautifulSoup) -> list[str]:
    raw = _meta(soup, "keywords", "citation_keywords", "DC.subject")
    if not raw:
        return []
    parts = re.split(r"[;,]", raw)
    return [p.strip().lower() for p in parts if p.strip()]


async def scrape_classical(url: str) -> ClassicalResult:
    started = time.monotonic()
    try:
        async with httpx.AsyncClient(timeout=HTTP_TIMEOUT, follow_redirects=True,
                                      headers={"User-Agent": "Mozilla/5.0 (compatible; LLMScraperBench/1.0)"}) as c:
            r = await c.get(url)
        bytes_dl = len(r.content)
        if r.status_code >= 400:
            return ClassicalResult(False, {}, bytes_dl,
                int((time.monotonic() - started) * 1000),
                f"HTTP {r.status_code}")
        html = r.text
    except httpx.HTTPError as e:
        return ClassicalResult(
            False, {}, 0, int((time.monotonic() - started) * 1000),
            f"network error: {e}",
        )

    # trafilatura main-content + metadata
    extracted = trafilatura.extract(
        html, include_comments=False, include_tables=False, with_metadata=False,
    ) or ""
    meta = trafilatura.extract_metadata(html)
    soup = BeautifulSoup(html, "lxml")

    title = (meta.title if meta else "") or _meta(soup, "citation_title", "og:title", "twitter:title") \
            or (soup.title.string.strip() if soup.title and soup.title.string else "")
    authors_raw = (meta.author if meta else "") or _meta(soup, "citation_author", "author", "DC.creator")
    authors = [a.strip() for a in re.split(r"[;,]| and ", authors_raw or "") if a.strip()]
    date = (meta.date if meta else "") or _meta(soup, "citation_publication_date", "article:published_time", "DC.date")
    venue = _meta(soup, "citation_journal_title", "og:site_name")
    doi = _meta(soup, "citation_doi", "DC.identifier")
    if doi:
        doi = doi.lower().replace("doi:", "").strip()

    # Naive abstract extraction: <meta name="description"> or trafilatura's first paragraph.
    abstract = _meta(soup, "citation_abstract", "DC.description", "description", "og:description") or ""
    if not abstract and extracted:
        abstract = extracted.split("\n\n")[0][:1000]

    image = _meta(soup, "og:image", "twitter:image", "citation_pdf_thumbnail_url")
    fields = {
        "title": title,
        "authors": authors,
        "abstract": abstract,
        "methodology": "",     # classical extractors don't infer methodology
        "conclusions": "",     # nor conclusions
        "keywords": _extract_keywords_from_meta(soup),
        "publication_year": _year_from_date(date),
        "venue": venue or None,
        "doi": doi or None,
        "image_url": image or "",
        "main_text": extracted[:5000],
    }
    duration = int((time.monotonic() - started) * 1000)
    return ClassicalResult(True, fields, len(html.encode("utf-8", errors="ignore")), duration)


def _year_from_date(date: str) -> int | None:
    if not date:
        return None
    m = re.search(r"(19|20)\d{2}", date)
    return int(m.group(0)) if m else None
