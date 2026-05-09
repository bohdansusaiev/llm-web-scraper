"""Phase 1 (Discovery) data — raw output from scientific APIs before extraction.

Lighter than ScientificPaper because methodology / conclusions / keywords come
from the LLM in Phase 2, not from these APIs."""
from typing import Optional
from pydantic import BaseModel, Field


class DiscoveredPaper(BaseModel):
    source: str = Field(description="'openalex' | 'semantic_scholar' | 'arxiv' | 'crossref'")
    doi: Optional[str] = Field(None, description="DOI normalized to lowercase, prefix stripped")
    title: str = ""
    authors: list[str] = Field(default_factory=list)
    publication_year: Optional[int] = None
    venue: Optional[str] = Field(None, description="Journal or conference name")
    abstract: str = ""
    landing_url: Optional[str] = Field(None, description="Publisher landing page")
    pdf_url: Optional[str] = Field(None, description="Open-access PDF URL if any")
    citation_count: Optional[int] = None
    is_open_access: bool = False

    @property
    def best_url(self) -> Optional[str]:
        """Preferred URL for Phase 2 extraction."""
        return self.pdf_url or self.landing_url
