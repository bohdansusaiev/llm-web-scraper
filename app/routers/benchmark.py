"""Benchmark endpoint — comparative analysis of LLM vs. classical scraping.
This is what produces the data for the thesis comparison chapter."""
from fastapi import APIRouter, Depends

from app.models.benchmark import (
    BenchmarkRequest, BenchmarkBatchRequest, BenchmarkResult, BenchmarkBatchSummary,
)
from app.routers._deps import require_user
from app.services.benchmark import run_benchmark, run_benchmark_batch

router = APIRouter(prefix="/benchmark", tags=["benchmark"])


@router.post("", response_model=BenchmarkResult)
async def benchmark_one(
    req: BenchmarkRequest,
    user_id: int = Depends(require_user),
) -> BenchmarkResult:
    return await run_benchmark(req)


@router.post("/batch", response_model=BenchmarkBatchSummary)
async def benchmark_batch(
    req: BenchmarkBatchRequest,
    user_id: int = Depends(require_user),
) -> BenchmarkBatchSummary:
    return await run_benchmark_batch(req)
