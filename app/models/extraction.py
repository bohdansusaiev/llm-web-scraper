"""Generic LLM extraction request/response — the diploma's core engine.

This is what makes the system 'general adaptive scraping': caller provides any
JSON schema + instruction, system returns matching structured data."""
from typing import Any, Optional
from pydantic import BaseModel, Field, HttpUrl


class GenericExtractRequest(BaseModel):
    """POST /scrape body. Caller supplies the schema and instruction."""
    url: HttpUrl
    output_schema: Optional[dict[str, Any]] = Field(default=None,
        description="JSON Schema (Pydantic-style) describing the desired output. "
                    "If omitted, returns a generic page summary.")
    instruction: Optional[str] = Field(default=None,
        description="Free-text instruction prepended to the extraction prompt. "
                    "Tell the LLM what to focus on and what to ignore.")
    language: str = Field(default="en",
        description="Output language for text fields. Currently 'en' or 'ua'.")
    use_cache: bool = Field(default=True,
        description="If true, returns a previously extracted result for this URL+schema.")


class GenericExtractResponse(BaseModel):
    url: str
    success: bool
    data: dict[str, Any] = Field(default_factory=dict,
        description="Structured output matching the requested schema.")
    markdown_preview: str = Field(default="",
        description="First ~500 chars of the extracted markdown — useful for debugging.")
    duration_ms: int = 0
    cached: bool = False
    error: str = ""
