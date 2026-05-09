"""Service layer for the generic /scrape endpoint — URL + schema -> structured data.
This is the layout-agnostic engine the diploma is built around."""
import logging
import time
from typing import Any, Optional

from app.core.crawler import fetch_markdown, truncate_markdown
from app.core.llm_extractor import extract as llm_extract
from app.db.cache import make_cache_key, get_cached, put_cached
from app.models.extraction import GenericExtractRequest, GenericExtractResponse

logger = logging.getLogger(__name__)


_TYPE_MAP = {
    "string": {"type": "string"}, "str": {"type": "string"},
    "number": {"type": "number"}, "float": {"type": "number"},
    "integer": {"type": "integer"}, "int": {"type": "integer"},
    "boolean": {"type": "boolean"}, "bool": {"type": "boolean"},
    "array": {"type": "array"}, "list": {"type": "array"},
    "object": {"type": "object"}, "dict": {"type": "object"},
}


def _normalize_schema(schema: Optional[dict[str, Any]]) -> Optional[dict[str, Any]]:
    """Accept either proper JSON Schema or the loose form {"field": "type"}.

    Loose form is what users naturally write in the UI:
        {"title": "string", "summary": "string", "tags": "array"}
    Convert it to a proper JSON Schema so DeepSeek respects it strictly."""
    if not schema or not isinstance(schema, dict):
        return None
    # Already proper JSON Schema (has top-level "type" or "properties")
    if isinstance(schema.get("type"), str) or "properties" in schema:
        return schema
    # Loose form — promote keys to properties
    props: dict[str, Any] = {}
    for key, val in schema.items():
        if isinstance(val, str):
            props[key] = _TYPE_MAP.get(val.lower().strip(), {"type": "string"})
        elif isinstance(val, dict):
            props[key] = val  # nested schema, pass through
        else:
            props[key] = {"type": "string"}
    return {
        "type": "object",
        "properties": props,
        "required": list(props.keys()),
        "additionalProperties": False,
    }


async def run_generic_extract(req: GenericExtractRequest) -> GenericExtractResponse:
    started = time.monotonic()
    url = str(req.url)
    schema = _normalize_schema(req.output_schema)

    cache_key = make_cache_key(url, schema, req.language)
    if req.use_cache:
        hit = get_cached(cache_key)
        if hit:
            data, md_preview = hit
            return GenericExtractResponse(
                url=url, success=True, data=data,
                markdown_preview=md_preview, cached=True,
                duration_ms=int((time.monotonic() - started) * 1000),
            )

    crawl = await fetch_markdown(url)
    if not crawl.success:
        return GenericExtractResponse(
            url=url, success=False, duration_ms=crawl.duration_ms,
            error=crawl.error or "crawl failed",
        )

    md = truncate_markdown(crawl.markdown)
    md_preview = md[:500]

    llm = await llm_extract(
        markdown=md,
        schema=schema,
        instruction=req.instruction,
    )
    duration_ms = int((time.monotonic() - started) * 1000)
    if not llm.success:
        return GenericExtractResponse(
            url=url, success=False, markdown_preview=md_preview,
            duration_ms=duration_ms, error=llm.error,
        )

    put_cached(cache_key, url, llm.data, markdown_preview=md_preview)
    return GenericExtractResponse(
        url=url, success=True, data=llm.data,
        markdown_preview=md_preview, duration_ms=duration_ms,
    )
