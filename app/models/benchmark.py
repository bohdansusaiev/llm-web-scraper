"""Benchmark models — comparative analysis of LLM vs. classical scraping.

This is the thesis chapter 'Comparative analysis' rendered as data."""
from typing import Any, Optional
from pydantic import BaseModel, Field, HttpUrl


class BenchmarkRequest(BaseModel):
    url: HttpUrl
    instruction: Optional[str] = Field(default=None,
        description="What the LLM should focus on. The classical scraper ignores this.")
    ground_truth: Optional[dict[str, Any]] = Field(default=None,
        description="Optional manually-labeled correct answers. Enables precision/recall.")


class ScraperResult(BaseModel):
    """One scraper's output for one URL."""
    method: str = Field(description="'llm' or 'classical'")
    success: bool
    fields: dict[str, Any] = Field(default_factory=dict,
        description="Whatever the scraper produced. Keys: title, abstract, authors, etc.")
    fields_populated: int = Field(default=0,
        description="Count of non-empty fields. Naive completeness signal.")
    duration_ms: int = 0
    bytes_downloaded: int = 0
    tokens_used: Optional[int] = Field(default=None,
        description="Total LLM tokens (input+output). None for classical.")
    estimated_cost_usd: float = 0.0
    error: str = ""


class FieldComparison(BaseModel):
    """Per-field side-by-side."""
    field: str
    llm_value: Any = None
    classical_value: Any = None
    ground_truth: Any = None
    llm_match: Optional[bool] = None
    classical_match: Optional[bool] = None


class BenchmarkResult(BaseModel):
    url: str
    llm: ScraperResult
    classical: ScraperResult
    fields: list[FieldComparison] = Field(default_factory=list)
    winner_completeness: str = Field(default="tie",
        description="'llm' | 'classical' | 'tie' — based on fields_populated.")
    winner_speed: str = "tie"


class BenchmarkBatchRequest(BaseModel):
    urls: list[HttpUrl] = Field(..., min_length=1, max_length=50)
    instruction: Optional[str] = None


class BenchmarkBatchSummary(BaseModel):
    """Aggregate across many URLs — what goes in your thesis table."""
    total_urls: int
    llm_success_rate: float
    classical_success_rate: float
    llm_avg_fields: float
    classical_avg_fields: float
    llm_avg_duration_ms: float
    classical_avg_duration_ms: float
    llm_total_cost_usd: float
    results: list[BenchmarkResult]
