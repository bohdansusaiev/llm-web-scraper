"""End-to-end research pipeline. Drives a job from topic to saved catalog,
streaming progress updates into research_jobs as it goes."""
import asyncio
import logging
import time
from collections import Counter
from datetime import datetime
from typing import Optional

from app.config import RELEVANCE_THRESHOLD
from app.db import jobs as jobs_db
from app.db import catalogs as catalogs_db
from app.models.catalog import (
    CatalogStats, ResearchRequest, ScientificCatalog, ScientificPaper,
    ExtractionFailureReason,
)
from app.models.discovery import DiscoveredPaper
from app.models.jobs import JobStatus
from app.services.discovery.aggregator import discover
from app.services.extraction.paper_extractor import extract_paper
from app.services.extraction.relevance import score_relevance
from app.services.extraction.translator import translate_paper

logger = logging.getLogger(__name__)


async def run_research_job(job_id: int, user_id: int, req: ResearchRequest) -> None:
    """Long-running task. Updates the research_jobs row as it proceeds.
    Never raises — failures are recorded on the job row."""
    started = time.monotonic()
    try:
        # --- Phase 1: Discovery ---
        jobs_db.update_job(job_id, status=JobStatus.DISCOVERING, progress=5,
                           message="Searching scientific APIs…")
        discovered = await discover(
            topic=req.topic,
            providers=req.providers,
            limit_per_provider=req.discovery_limit,
            min_year=req.min_year,
        )
        logger.info("job %d: discovered %d papers", job_id, len(discovered))
        if not discovered:
            jobs_db.update_job(
                job_id, status=JobStatus.FAILED, progress=100,
                error="No papers found by any discovery provider for this topic.",
            )
            return

        # Optional: filter to OA-only before deep extraction
        candidates = discovered
        if req.open_access_only:
            with_url = [p for p in discovered if (p.pdf_url or p.landing_url)]
            candidates = with_url or discovered  # don't strand the job if everything filters out

        jobs_db.update_job(
            job_id, progress=20,
            message=f"Found {len(discovered)} papers, scoring relevance…",
        )

        # --- Phase 1.5: Relevance scoring ---
        jobs_db.update_job(job_id, status=JobStatus.FILTERING, progress=25)
        scores = await score_relevance(req.topic, candidates)

        # Sort + threshold + topK
        ranked: list[tuple[DiscoveredPaper, float]] = sorted(
            ((p, scores.get(i, 0.0)) for i, p in enumerate(candidates)),
            key=lambda x: x[1], reverse=True,
        )
        kept = [(p, s) for p, s in ranked if s >= RELEVANCE_THRESHOLD]
        if not kept:
            # threshold was too aggressive — fall back to top-K of all
            kept = ranked[: req.max_papers]
        top = kept[: req.max_papers]
        relevance_filtered = len(kept)

        jobs_db.update_job(
            job_id, status=JobStatus.EXTRACTING, progress=35,
            message=f"Deeply extracting {len(top)} top papers…",
        )

        # --- Phase 2: Deep extraction (parallel, but capped) ---
        sem = asyncio.Semaphore(4)  # don't hammer the LLM or sites

        async def _extract_one(d: DiscoveredPaper, score: float) -> ScientificPaper:
            async with sem:
                return await extract_paper(d, relevance_score=score)

        papers: list[ScientificPaper] = []
        completed = 0
        # gather as completed for live progress
        tasks = [asyncio.create_task(_extract_one(d, s)) for d, s in top]
        for task in asyncio.as_completed(tasks):
            paper = await task
            papers.append(paper)
            completed += 1
            pct = 35 + int(50 * completed / max(1, len(tasks)))
            jobs_db.update_job(
                job_id, progress=pct,
                message=f"Extracted {completed}/{len(tasks)} papers",
            )

        # --- Phase 3: Translation (optional) ---
        if req.language != "en":
            jobs_db.update_job(
                job_id, status=JobStatus.TRANSLATING, progress=88,
                message=f"Translating to {req.language}…",
            )
            translated: list[ScientificPaper] = []
            tx_sem = asyncio.Semaphore(4)

            async def _tx(p: ScientificPaper) -> ScientificPaper:
                async with tx_sem:
                    return await translate_paper(p, req.language)

            translated = await asyncio.gather(*[_tx(p) for p in papers])
            papers = list(translated)

        # --- Stats ---
        failure_counts = Counter(p.failure_reason.value for p in papers
                                 if p.failure_reason != ExtractionFailureReason.NONE)
        successful = [p for p in papers if p.failure_reason == ExtractionFailureReason.NONE]
        # Sort final list by relevance descending
        papers.sort(key=lambda p: p.relevance_score, reverse=True)

        stats = CatalogStats(
            discovered=len(discovered),
            after_dedupe=len(discovered),  # already deduped at discovery
            relevance_filtered=relevance_filtered,
            deeply_extracted=len(successful),
            failed=len(papers) - len(successful),
            duration_seconds=round(time.monotonic() - started, 2),
            failure_breakdown=dict(failure_counts),
        )

        catalog = ScientificCatalog(
            user_id=user_id,
            topic=req.topic,
            language=req.language,
            created_at=datetime.now(),
            papers=papers,
            stats=stats,
        )

        jobs_db.update_job(job_id, status=JobStatus.SAVING, progress=95,
                           message="Saving catalog…")
        catalog_id = catalogs_db.save_catalog(user_id, catalog)
        jobs_db.update_job(
            job_id, status=JobStatus.COMPLETED, progress=100,
            message=f"Done. {len(successful)} papers extracted.",
            catalog_id=catalog_id,
        )
        logger.info("job %d: completed catalog %d in %.1fs",
                    job_id, catalog_id, stats.duration_seconds)
    except Exception as e:  # ensure the job is marked failed, never stuck
        logger.exception("job %d failed: %s", job_id, e)
        jobs_db.update_job(
            job_id, status=JobStatus.FAILED, progress=100,
            error=f"Pipeline error: {e}",
        )
