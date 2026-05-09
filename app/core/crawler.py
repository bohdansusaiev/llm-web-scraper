"""URL → clean markdown. Two strategies, tried in order:

1. Crawl4AI (Playwright) — handles JS-rendered pages.
2. Jina Reader (r.jina.ai) — lightweight HTTP fallback; bypasses many bot checks
   and works well on static pages / academic sites that block headless browsers.

The fallback is the thesis's 'adaptive, low-resource' claim: we don't give up when
one method fails — we try a simpler, cheaper alternative automatically.
"""
import time
from dataclasses import dataclass
from typing import Optional

import httpx
from crawl4ai import AsyncWebCrawler, CacheMode
from crawl4ai.async_configs import CrawlerRunConfig

from app.config import CRAWLER_TIMEOUT_MS, CRAWLER_WORD_THRESHOLD, HTTP_TIMEOUT

_JINA_MIN_CHARS = 200  # Jina result shorter than this is treated as an error page


@dataclass
class CrawlResult:
    success: bool
    url: str
    markdown: str = ""
    html_size: int = 0
    duration_ms: int = 0
    status_code: Optional[int] = None
    error: str = ""


async def fetch_markdown(url: str) -> CrawlResult:
    """Fetch a URL and return its main content as markdown.

    Tries Crawl4AI first (full JS rendering). Falls back to Jina Reader when
    Crawl4AI fails or returns near-empty content (bot protection, timeout, etc.)."""
    result = await _fetch_via_crawl4ai(url)
    if result.success and len(result.markdown.strip()) > _JINA_MIN_CHARS:
        return result
    jina = await _fetch_via_jina(url)
    if jina.success and len(jina.markdown.strip()) > len(result.markdown.strip()):
        return jina
    return result


async def _fetch_via_crawl4ai(url: str) -> CrawlResult:
    started = time.monotonic()
    run_cfg = CrawlerRunConfig(
        cache_mode=CacheMode.BYPASS,
        word_count_threshold=CRAWLER_WORD_THRESHOLD,
        page_timeout=CRAWLER_TIMEOUT_MS,
        wait_until="domcontentloaded",
        verbose=False,
    )
    try:
        async with AsyncWebCrawler(verbose=False) as crawler:
            result = await crawler.arun(url=url, config=run_cfg)
            duration_ms = int((time.monotonic() - started) * 1000)
            if not result.success:
                return CrawlResult(
                    success=False, url=url, duration_ms=duration_ms,
                    status_code=getattr(result, "status_code", None),
                    error=result.error_message or "Unknown crawler error",
                )
            md = ""
            if hasattr(result, "markdown") and result.markdown:
                md = getattr(result.markdown, "raw_markdown", None) or str(result.markdown)
            html_size = len(result.html or "") if hasattr(result, "html") else 0
            return CrawlResult(
                success=True, url=url, markdown=md or "",
                html_size=html_size, duration_ms=duration_ms,
                status_code=getattr(result, "status_code", 200),
            )
    except Exception as e:
        return CrawlResult(
            success=False, url=url,
            duration_ms=int((time.monotonic() - started) * 1000),
            error=f"crawler exception: {e}",
        )


async def _fetch_via_jina(url: str) -> CrawlResult:
    """Jina Reader API: prepend r.jina.ai/ to any URL → clean markdown.
    Free, no API key needed, works on most static and semi-dynamic pages."""
    started = time.monotonic()
    try:
        async with httpx.AsyncClient(timeout=HTTP_TIMEOUT, follow_redirects=True) as client:
            r = await client.get(
                f"https://r.jina.ai/{url}",
                headers={
                    "Accept": "text/markdown",
                    "X-Return-Format": "markdown",
                    "User-Agent": "Mozilla/5.0 (compatible; LLMScraperDiploma/1.0)",
                },
            )
        duration_ms = int((time.monotonic() - started) * 1000)
        if r.status_code >= 400:
            return CrawlResult(
                success=False, url=url, duration_ms=duration_ms,
                status_code=r.status_code, error=f"Jina HTTP {r.status_code}",
            )
        return CrawlResult(
            success=True, url=url, markdown=r.text,
            html_size=len(r.content), duration_ms=duration_ms,
            status_code=r.status_code,
        )
    except Exception as e:
        return CrawlResult(
            success=False, url=url,
            duration_ms=int((time.monotonic() - started) * 1000),
            error=f"jina exception: {e}",
        )


def detect_block_reason(markdown: str) -> Optional[str]:
    """Best-effort sniff: did we hit a login wall / paywall / bot challenge?

    Returns a string from ExtractionFailureReason if detected, else None."""
    if not markdown:
        return "extraction_empty"
    lo = markdown.lower()
    login_signals = ("sign in to read", "log in to read", "please sign in", "login required",
                     "create a free account to continue", "create an account to read")
    paywall_signals = ("purchase access", "buy this article", "subscribe to read",
                       "get full access", "access through your institution")
    bot_signals = ("verify you are human", "checking your browser", "ddos protection by",
                   "cloudflare", "captcha", "are you a robot")
    if any(s in lo for s in login_signals):
        return "login_wall"
    if any(s in lo for s in paywall_signals):
        return "paywall"
    if any(s in lo for s in bot_signals) and len(markdown) < 2000:
        return "bot_protection"
    return None


def truncate_markdown(markdown: str, max_chars: int = 20_000) -> str:
    """Cap markdown size before sending to LLM — controls cost.
    20k chars ≈ 5k tokens for English. Most papers' abstract+intro+conclusion fit."""
    if len(markdown) <= max_chars:
        return markdown
    return markdown[:max_chars] + "\n\n[... truncated ...]"
