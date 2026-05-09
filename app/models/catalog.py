"""Scientific catalog domain models — Phase 2 output and user-facing artifact."""
from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class ExtractionFailureReason(str, Enum):
    """Why Phase 2 may fail on a given paper. Tracked per-paper for thesis stats."""
    NONE = "none"
    PAYWALL = "paywall"
    LOGIN_WALL = "login_wall"
    BOT_PROTECTION = "bot_protection"
    TIMEOUT = "timeout"
    NETWORK_ERROR = "network_error"
    EXTRACTION_EMPTY = "extraction_empty"
    LLM_ERROR = "llm_error"


class Author(BaseModel):
    name: str = ""
    affiliation: Optional[str] = None
    orcid: Optional[str] = None


class ResearchRequest(BaseModel):
    """User input — the only thing they fill in to run a research job."""
    topic: str = Field(..., min_length=3, max_length=300,
        description="Free-text research topic, e.g. 'Machine learning in web scraping'")
    max_papers: int = Field(default=10, ge=1, le=50,
        description="How many top papers to deeply extract (Phase 2). Caps LLM cost.")
    discovery_limit: int = Field(default=30, ge=5, le=100,
        description="How many candidates Phase 1 fetches per provider before relevance filtering.")
    providers: list[str] = Field(default=["openalex", "crossref"],
        description="Subset of {openalex, crossref, semantic_scholar}.")
    min_year: Optional[int] = Field(default=None, ge=1900,
        description="Filter out papers older than this year.")
    open_access_only: bool = Field(default=True,
        description="Only attempt deep extraction on papers with an open-access URL.")
    language: str = Field(default="en",
        description="'en' or 'ua'. Triggers post-extraction translation of text fields.")


class ScientificPaper(BaseModel):
    """The deep-extraction schema. Fields filled by API + LLM together."""
    # --- Identity (from Phase 1) ---
    doi: Optional[str] = None
    title: str = ""
    authors: list[Author] = Field(default_factory=list)
    publication_year: Optional[int] = None
    venue: Optional[str] = None
    url: str = Field(default="", description="Canonical URL used for Phase 2 extraction")

    # --- Content (LLM-extracted from page markdown in Phase 2) ---
    abstract: str = Field(default="",
        description="Paper abstract; from API when available, else extracted from page")
    methodology: str = Field(default="",
        description="2-4 sentences on the core method, dataset, or experimental setup")
    conclusions: str = Field(default="",
        description="2-4 sentences on findings and stated implications")
    keywords: list[str] = Field(default_factory=list,
        description="3-8 lowercase keywords. Prefer concrete techniques over generic words.")

    # --- Quality / provenance ---
    image_url: str = Field(default="",
        description="Lead/figure image URL if visible on the page (e.g. paper figure thumbnail).")
    citation_count: Optional[int] = None
    is_open_access: bool = False
    relevance_score: float = Field(default=0.0, ge=0.0, le=1.0,
        description="LLM-judged relevance to the topic. 0=off-topic, 1=directly on-topic.")
    extraction_source: str = Field(default="",
        description="'api' if abstract came from API only, 'crawl' if extracted from page.")
    failure_reason: ExtractionFailureReason = ExtractionFailureReason.NONE
    language: str = Field(default="en", description="Language of the text fields after translation.")


class CatalogStats(BaseModel):
    discovered: int = 0
    after_dedupe: int = 0
    relevance_filtered: int = 0
    deeply_extracted: int = 0
    failed: int = 0
    duration_seconds: float = 0.0
    failure_breakdown: dict[str, int] = Field(default_factory=dict,
        description="ExtractionFailureReason -> count")


class ScientificCatalog(BaseModel):
    id: Optional[int] = None
    user_id: Optional[int] = None
    topic: str
    language: str = "en"
    created_at: datetime
    papers: list[ScientificPaper] = Field(default_factory=list)
    stats: CatalogStats = Field(default_factory=CatalogStats)


class CatalogSummary(BaseModel):
    """Lightweight list-view of a catalog (no paper bodies)."""
    id: int
    topic: str
    language: str
    created_at: datetime
    paper_count: int
