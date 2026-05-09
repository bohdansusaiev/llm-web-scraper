"""Generic LLM extractor — takes a markdown blob + a JSON schema + an instruction
and returns structured data. This is the engine the thesis is about.

Implementation note: we call DeepSeek via the OpenAI-compatible HTTP API
directly (httpx). This keeps the extractor model-agnostic — swapping providers
is one URL change — and gives us token usage for the cost benchmark, which
crawl4ai's LLMExtractionStrategy hides."""
import json
import re
import time
from typing import Any, Optional
from dataclasses import dataclass, field

import httpx

from app.config import (
    DEEPSEEK_API_KEY, LLM_BASE_URL, LLM_TEMPERATURE, HTTP_TIMEOUT,
)
from app.core.prompts import GENERIC_EXTRACTION_INSTRUCTION


# DeepSeek-chat pricing (per 1M tokens). Keep in one place for the benchmark.
COST_INPUT_PER_MTOK = 0.27
COST_OUTPUT_PER_MTOK = 1.10


@dataclass
class LLMExtractResult:
    success: bool
    data: dict[str, Any] = field(default_factory=dict)
    raw_text: str = ""
    input_tokens: int = 0
    output_tokens: int = 0
    duration_ms: int = 0
    error: str = ""

    @property
    def total_tokens(self) -> int:
        return self.input_tokens + self.output_tokens

    @property
    def cost_usd(self) -> float:
        return (
            self.input_tokens * COST_INPUT_PER_MTOK / 1_000_000
            + self.output_tokens * COST_OUTPUT_PER_MTOK / 1_000_000
        )


def _build_user_message(markdown: str, schema: Optional[dict[str, Any]]) -> str:
    parts = []
    if schema:
        parts.append("DESIRED OUTPUT SCHEMA (JSON Schema):")
        parts.append(json.dumps(schema, ensure_ascii=False, indent=2))
        parts.append("")
    parts.append("PAGE MARKDOWN:")
    parts.append(markdown)
    return "\n".join(parts)


def _strip_code_fence(text: str) -> str:
    """LLMs sometimes wrap JSON in ```json ... ``` despite being told not to."""
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    return text.strip()


async def extract(
    markdown: str,
    *,
    schema: Optional[dict[str, Any]] = None,
    instruction: Optional[str] = None,
    model: str = "deepseek-chat",
) -> LLMExtractResult:
    """Run one LLM extraction call. Returns structured data + token usage."""
    if not markdown.strip():
        return LLMExtractResult(success=False, error="empty markdown input")

    # DeepSeek's json_object response_format requires the literal word "json"
    # somewhere in the prompt. Always ensure it's there, even if the caller's
    # custom instruction omits it.
    sys_prompt = instruction or GENERIC_EXTRACTION_INSTRUCTION
    if "json" not in sys_prompt.lower():
        sys_prompt = sys_prompt.rstrip() + "\n\nReturn ONLY a valid json object matching the schema."

    body = {
        "model": model,
        "temperature": LLM_TEMPERATURE,
        "response_format": {"type": "json_object"},
        "messages": [
            {"role": "system", "content": sys_prompt},
            {"role": "user", "content": _build_user_message(markdown, schema)},
        ],
    }

    started = time.monotonic()
    try:
        async with httpx.AsyncClient(timeout=HTTP_TIMEOUT * 4) as client:
            r = await client.post(
                f"{LLM_BASE_URL}/chat/completions",
                json=body,
                headers={"Authorization": f"Bearer {DEEPSEEK_API_KEY}"},
            )
        duration_ms = int((time.monotonic() - started) * 1000)
        if r.status_code != 200:
            return LLMExtractResult(
                success=False, duration_ms=duration_ms,
                error=f"LLM HTTP {r.status_code}: {r.text[:200]}",
            )
        payload = r.json()
        content = payload["choices"][0]["message"]["content"]
        usage = payload.get("usage", {})
        in_tok = usage.get("prompt_tokens", 0)
        out_tok = usage.get("completion_tokens", 0)
    except (httpx.HTTPError, KeyError, ValueError) as e:
        return LLMExtractResult(
            success=False,
            duration_ms=int((time.monotonic() - started) * 1000),
            error=f"LLM call failed: {e}",
        )

    raw = _strip_code_fence(content)
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        return LLMExtractResult(
            success=False, raw_text=raw, duration_ms=duration_ms,
            input_tokens=in_tok, output_tokens=out_tok,
            error=f"LLM returned invalid JSON: {e}",
        )

    return LLMExtractResult(
        success=True, data=data, raw_text=raw,
        input_tokens=in_tok, output_tokens=out_tok, duration_ms=duration_ms,
    )
