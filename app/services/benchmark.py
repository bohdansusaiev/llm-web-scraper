"""Benchmark service — run BOTH the LLM scraper and the classical baseline on
the same URL(s), produce side-by-side metrics for the thesis.

This is what answers the diploma's 'Comparative analysis of LLM vs. classical
methods' result-line."""
import asyncio
import logging
from typing import Any, Optional

from app.core.crawler import fetch_markdown, truncate_markdown
from app.core.llm_extractor import extract as llm_extract
from app.core.prompts import BENCHMARK_DEFAULT_INSTRUCTION
from app.services.classical_scraper import scrape_classical
from app.services.extraction.paper_extractor import PAPER_LLM_SCHEMA
from app.models.benchmark import (
    BenchmarkRequest, BenchmarkBatchRequest, BenchmarkResult,
    BenchmarkBatchSummary, FieldComparison, ScraperResult,
)

logger = logging.getLogger(__name__)


# Fields we compare side-by-side. Both scrapers produce these.
COMPARED_FIELDS = ("title", "authors", "abstract", "methodology", "conclusions",
                    "keywords", "publication_year", "venue", "doi", "image_url")


async def run_benchmark(req: BenchmarkRequest) -> BenchmarkResult:
    """Run both scrapers on one URL in parallel."""
    url = str(req.url)
    instruction = req.instruction or BENCHMARK_DEFAULT_INSTRUCTION

    llm_task = asyncio.create_task(_run_llm(url, instruction))
    classical_task = asyncio.create_task(_run_classical(url))
    llm_res, classical_res = await asyncio.gather(llm_task, classical_task)

    fields = _compare_fields(llm_res, classical_res, req.ground_truth)

    winner_complete = "tie"
    if llm_res.fields_populated > classical_res.fields_populated:
        winner_complete = "llm"
    elif classical_res.fields_populated > llm_res.fields_populated:
        winner_complete = "classical"

    winner_speed = "tie"
    if llm_res.duration_ms < classical_res.duration_ms:
        winner_speed = "llm"
    elif classical_res.duration_ms < llm_res.duration_ms:
        winner_speed = "classical"

    return BenchmarkResult(
        url=url, llm=llm_res, classical=classical_res, fields=fields,
        winner_completeness=winner_complete, winner_speed=winner_speed,
    )


async def run_benchmark_batch(req: BenchmarkBatchRequest) -> BenchmarkBatchSummary:
    sem = asyncio.Semaphore(3)

    async def _one(u) -> BenchmarkResult:
        async with sem:
            return await run_benchmark(BenchmarkRequest(url=u, instruction=req.instruction))

    results = await asyncio.gather(*[_one(u) for u in req.urls])

    total = len(results)
    llm_ok = sum(1 for r in results if r.llm.success)
    cl_ok = sum(1 for r in results if r.classical.success)
    return BenchmarkBatchSummary(
        total_urls=total,
        llm_success_rate=round(llm_ok / total, 3),
        classical_success_rate=round(cl_ok / total, 3),
        llm_avg_fields=round(sum(r.llm.fields_populated for r in results) / total, 2),
        classical_avg_fields=round(sum(r.classical.fields_populated for r in results) / total, 2),
        llm_avg_duration_ms=round(sum(r.llm.duration_ms for r in results) / total, 1),
        classical_avg_duration_ms=round(sum(r.classical.duration_ms for r in results) / total, 1),
        llm_total_cost_usd=round(sum(r.llm.estimated_cost_usd for r in results), 5),
        results=results,
    )


# ---------- Internals ----------

async def _run_llm(url: str, instruction: str) -> ScraperResult:
    crawl = await fetch_markdown(url)
    if not crawl.success:
        return ScraperResult(
            method="llm", success=False, fields={}, fields_populated=0,
            duration_ms=crawl.duration_ms, bytes_downloaded=0,
            error=crawl.error,
        )
    md = truncate_markdown(crawl.markdown)
    llm = await llm_extract(markdown=md, schema=PAPER_LLM_SCHEMA, instruction=instruction)
    if not llm.success:
        return ScraperResult(
            method="llm", success=False, fields={},
            fields_populated=0,
            duration_ms=crawl.duration_ms + llm.duration_ms,
            bytes_downloaded=crawl.html_size,
            tokens_used=llm.total_tokens,
            estimated_cost_usd=round(llm.cost_usd, 6),
            error=llm.error,
        )
    fields = _normalize_fields(llm.data)
    return ScraperResult(
        method="llm", success=True, fields=fields,
        fields_populated=_count_populated(fields),
        duration_ms=crawl.duration_ms + llm.duration_ms,
        bytes_downloaded=crawl.html_size,
        tokens_used=llm.total_tokens,
        estimated_cost_usd=round(llm.cost_usd, 6),
    )


async def _run_classical(url: str) -> ScraperResult:
    res = await scrape_classical(url)
    return ScraperResult(
        method="classical",
        success=res.success,
        fields=res.fields,
        fields_populated=_count_populated(res.fields),
        duration_ms=res.duration_ms,
        bytes_downloaded=res.bytes_downloaded,
        tokens_used=None,
        estimated_cost_usd=0.0,
        error=res.error,
    )


def _normalize_fields(data: dict[str, Any]) -> dict[str, Any]:
    """Make LLM output shape comparable to classical output."""
    authors = data.get("authors") or []
    if isinstance(authors, list):
        authors = [a.get("name") if isinstance(a, dict) else str(a) for a in authors if a]
    return {
        "title": data.get("title", ""),
        "authors": authors,
        "abstract": data.get("abstract", ""),
        "methodology": data.get("methodology", ""),
        "conclusions": data.get("conclusions", ""),
        "keywords": data.get("keywords", []) or [],
        "publication_year": data.get("publication_year"),
        "venue": data.get("venue"),
        "doi": data.get("doi"),
        "image_url": data.get("image_url", "") or "",
    }


def _count_populated(fields: dict[str, Any]) -> int:
    n = 0
    for k in COMPARED_FIELDS:
        v = fields.get(k)
        if v is None or v == "" or v == [] or v == {}:
            continue
        n += 1
    return n


def _compare_fields(
    llm: ScraperResult,
    classical: ScraperResult,
    ground_truth: Optional[dict[str, Any]],
) -> list[FieldComparison]:
    out: list[FieldComparison] = []
    for f in COMPARED_FIELDS:
        lv = llm.fields.get(f)
        cv = classical.fields.get(f)
        gv = (ground_truth or {}).get(f)
        out.append(FieldComparison(
            field=f,
            llm_value=lv, classical_value=cv, ground_truth=gv,
            llm_match=_match(lv, gv) if gv is not None else None,
            classical_match=_match(cv, gv) if gv is not None else None,
        ))
    return out


def _match(value: Any, truth: Any) -> bool:
    """Loose match: case-insensitive substring for strings, set-equal for lists."""
    if value is None or truth is None:
        return False
    if isinstance(truth, list):
        if not isinstance(value, list):
            return False
        return {str(v).lower() for v in value} >= {str(t).lower() for t in truth}
    return str(truth).lower() in str(value).lower()
